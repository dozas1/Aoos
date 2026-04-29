from __future__ import annotations

import time
import uuid

import pytest

from app import flow
from app.metrics import compute_H
from app.models import Cycle, Rule, State


def _cycle(text: str, escalated=False, decided=True, true_type=None, proposed="σ.s", matched=None):
    return Cycle(
        id=str(uuid.uuid4()),
        text=text,
        proposed_type=proposed,
        matched_rule_id=matched,
        escalated=escalated,
        user_decision=False if escalated and decided else (True if decided else None),
        true_type=true_type if escalated else (proposed if decided else None),
        timestamp=time.time(),
    )


def _rule(pattern: str, type_: str, hits: int = 0, correct: int = 0):
    return Rule(
        id=str(uuid.uuid4()),
        pattern=pattern,
        type=type_,
        hits=hits,
        correct=correct,
    )


def test_classify_first_match_wins():
    rules = [_rule(r"(?i)bug", "σ.s", hits=10, correct=10),
             _rule(r"(?i)bug", "σ.c", hits=10, correct=1)]
    proposed, matched = flow.classify("hay un bug", rules)
    assert proposed == "σ.s"
    assert matched == rules[0].id


def test_classify_no_match_escalates():
    proposed, matched = flow.classify("texto cualquiera", [])
    assert proposed == "UNKNOWN"
    assert matched is None


def test_compute_H_empty():
    U, Q, H = compute_H([])
    assert (U, Q, H) == (1.0, 0.0, 0.0)


def test_compute_H_all_correct():
    cycles = [_cycle(f"t{i}") for i in range(50)]
    U, Q, H = compute_H(cycles)
    assert U == 0.0
    assert Q == 1.0
    assert H == 1.0


def test_compute_H_half_escalated():
    cycles = [_cycle(f"t{i}", escalated=(i % 2 == 0), true_type="σ.c") for i in range(50)]
    U, Q, H = compute_H(cycles)
    assert U == pytest.approx(0.5)
    assert Q == pytest.approx(0.5)
    assert H == pytest.approx(0.25)


def test_propose_rules_finds_keyword():
    state = State()
    state.cycles = [
        _cycle("deploy a staging", escalated=True, true_type="σ.c"),
        _cycle("deploy a prod", escalated=True, true_type="σ.c"),
        _cycle("deploy ahora", escalated=True, true_type="σ.c"),
    ]
    proposals = flow.propose_rules(state)
    deploys = [p for p in proposals if "deploy" in p.pattern]
    assert deploys, f"expected a 'deploy' proposal, got {[p.pattern for p in proposals]}"
    assert deploys[0].type == "σ.c"


def test_propose_rules_skips_unselective():
    state = State()
    state.cycles = [
        _cycle("revisa el tema X", escalated=True, true_type="σ.c"),
        _cycle("revisa el tema Y", escalated=True, true_type="σ.c"),
        _cycle("revisa el tema Z", escalated=True, true_type="σ.c"),
        _cycle("revisa esto", escalated=True, true_type="σ.s"),
        _cycle("revisa lo otro", escalated=True, true_type="σ.s"),
        _cycle("revisa aquí", escalated=True, true_type="σ.s"),
    ]
    proposals = flow.propose_rules(state)
    patterns = [p.pattern for p in proposals]
    assert not any("revisa" in p for p in patterns), patterns


def test_propose_rules_skips_existing_pattern():
    state = State()
    state.rules = [_rule(r"(?i)\bdeploy\b", "σ.c")]
    state.cycles = [
        _cycle("deploy a staging", escalated=True, true_type="σ.c"),
        _cycle("deploy a prod", escalated=True, true_type="σ.c"),
        _cycle("deploy ahora", escalated=True, true_type="σ.c"),
    ]
    proposals = flow.propose_rules(state)
    assert not any("deploy" in p.pattern for p in proposals)


def test_apply_proposal_records_baseline():
    state = State()
    state.cycles = [_cycle(f"t{i}", escalated=False) for i in range(10)]
    proposal = flow.Proposal(
        id=str(uuid.uuid4()),
        pattern=r"(?i)\bdeploy\b",
        type="σ.c",
    )
    state.proposals = [proposal]
    rule = flow.apply_proposal(state, proposal.id)
    assert rule.applied_at_cycle == 10
    assert rule.H_at_apply == pytest.approx(1.0)
    assert proposal.id not in [p.id for p in state.proposals]


def test_auto_revert_when_H_drops():
    state = State()
    # 10 good cycles
    state.cycles = [_cycle(f"t{i}") for i in range(10)]
    rule = _rule(r"(?i)\bx\b", "σ.s")
    rule.applied_at_cycle = 10
    rule.H_at_apply = 1.0
    state.rules = [rule]
    # 10 escalated cycles after apply -> H drops
    state.cycles += [_cycle(f"x{i}", escalated=True, true_type="σ.c") for i in range(10)]
    reverted = flow.auto_revert_pass(state)
    assert rule.id in reverted
    assert rule.id not in [r.id for r in state.rules]
    assert state.revert_log


def test_auto_revert_graduates_when_H_holds():
    state = State()
    state.cycles = [_cycle(f"t{i}") for i in range(10)]
    rule = _rule(r"(?i)\bx\b", "σ.s")
    rule.applied_at_cycle = 10
    rule.H_at_apply = 0.9
    state.rules = [rule]
    state.cycles += [_cycle(f"x{i}") for i in range(10)]
    reverted = flow.auto_revert_pass(state)
    assert reverted == []
    survivor = state.rules[0]
    assert survivor.applied_at_cycle is None
    assert survivor.H_at_apply is None


def test_apply_decision_updates_rule_stats():
    state = State()
    rule = _rule(r"(?i)bug", "σ.s")
    state.rules = [rule]
    cycle = flow.open_cycle("hay un bug", state.rules)
    state.cycles.append(cycle)
    flow.apply_decision(state, cycle.id, accepted=True, true_type=None)
    assert rule.hits == 1
    assert rule.correct == 1


def test_apply_decision_correction_marks_escalated():
    state = State()
    rule = _rule(r"(?i)bug", "σ.s")
    state.rules = [rule]
    cycle = flow.open_cycle("hay un bug raro", state.rules)
    state.cycles.append(cycle)
    flow.apply_decision(state, cycle.id, accepted=False, true_type="σ.c")
    assert cycle.escalated is True
    assert cycle.true_type == "σ.c"
    assert rule.hits == 1
    assert rule.correct == 0
