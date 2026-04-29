from __future__ import annotations

import re
import time
import uuid
from collections import defaultdict

from .metrics import compute_H
from .models import Cycle, HSnapshot, Proposal, Rule, State

OBSERVATION_WINDOW = 10
H_DROP_TOLERANCE = 0.05
PROPOSE_EVERY = 10
MIN_TOKEN_LEN = 3
MIN_GROUP_SUPPORT = 3
MAX_OTHER_SUPPORT = 1
TOKEN_RE = re.compile(r"[a-záéíóúñ]+", re.IGNORECASE)


def _rule_score(r: Rule) -> tuple[float, int]:
    accuracy = (r.correct / r.hits) if r.hits else 0.5
    return (accuracy, r.hits)


def classify(text: str, rules: list[Rule]) -> tuple[str, str | None]:
    ordered = sorted(rules, key=_rule_score, reverse=True)
    for r in ordered:
        try:
            if re.search(r.pattern, text):
                return r.type, r.id
        except re.error:
            continue
    return "UNKNOWN", None


def open_cycle(text: str, rules: list[Rule]) -> Cycle:
    proposed_type, matched_rule_id = classify(text, rules)
    return Cycle(
        id=str(uuid.uuid4()),
        text=text,
        proposed_type=proposed_type,
        matched_rule_id=matched_rule_id,
        escalated=matched_rule_id is None,
        timestamp=time.time(),
    )


def apply_decision(
    state: State,
    cycle_id: str,
    accepted: bool,
    true_type: str | None,
) -> Cycle:
    cycle = next((c for c in state.cycles if c.id == cycle_id), None)
    if cycle is None:
        raise KeyError(cycle_id)
    if cycle.user_decision is not None:
        return cycle

    cycle.user_decision = accepted
    if not accepted:
        cycle.escalated = True
        cycle.true_type = true_type
    else:
        cycle.true_type = cycle.proposed_type

    if cycle.matched_rule_id is not None:
        rule = next((r for r in state.rules if r.id == cycle.matched_rule_id), None)
        if rule is not None:
            rule.hits += 1
            if accepted:
                rule.correct += 1
    return cycle


def _tokens(text: str) -> set[str]:
    return {t.lower() for t in TOKEN_RE.findall(text) if len(t) >= MIN_TOKEN_LEN}


def propose_rules(state: State) -> list[Proposal]:
    cycles = state.cycles[-50:]
    escalated = [c for c in cycles if c.escalated and c.true_type]
    if len(escalated) < MIN_GROUP_SUPPORT:
        return []

    by_type: dict[str, list[Cycle]] = defaultdict(list)
    for c in escalated:
        by_type[c.true_type].append(c)

    existing_patterns = {r.pattern for r in state.rules}
    pending_patterns = {p.pattern for p in state.proposals}
    new_proposals: list[Proposal] = []

    for true_type, group in by_type.items():
        if len(group) < MIN_GROUP_SUPPORT:
            continue
        token_support: dict[str, list[str]] = defaultdict(list)
        for c in group:
            for tok in _tokens(c.text):
                token_support[tok].append(c.id)

        for tok, evidence_ids in token_support.items():
            if len(evidence_ids) < MIN_GROUP_SUPPORT:
                continue
            other_support = 0
            for other_type, other_group in by_type.items():
                if other_type == true_type:
                    continue
                for c in other_group:
                    if tok in _tokens(c.text):
                        other_support += 1
            if other_support > MAX_OTHER_SUPPORT:
                continue

            pattern = rf"(?i)\b{re.escape(tok)}\b"
            if pattern in existing_patterns or pattern in pending_patterns:
                continue

            new_proposals.append(
                Proposal(
                    id=str(uuid.uuid4()),
                    pattern=pattern,
                    type=true_type,
                    evidence_cycle_ids=evidence_ids,
                )
            )
            existing_patterns.add(pattern)

    return new_proposals


def apply_proposal(state: State, proposal_id: str) -> Rule:
    proposal = next((p for p in state.proposals if p.id == proposal_id), None)
    if proposal is None:
        raise KeyError(proposal_id)
    _, _, H_now = compute_H(state.cycles)
    rule = Rule(
        id=str(uuid.uuid4()),
        pattern=proposal.pattern,
        type=proposal.type,
        source="auto",
        applied_at_cycle=len(state.cycles),
        H_at_apply=H_now,
    )
    state.rules.append(rule)
    state.proposals = [p for p in state.proposals if p.id != proposal_id]
    return rule


def discard_proposal(state: State, proposal_id: str) -> None:
    state.proposals = [p for p in state.proposals if p.id != proposal_id]


def remove_rule(state: State, rule_id: str) -> None:
    state.rules = [r for r in state.rules if r.id != rule_id]


def auto_revert_pass(state: State) -> list[str]:
    """Check rules with applied_at_cycle set; revert or graduate when window elapsed."""
    reverted: list[str] = []
    cycles_now = len(state.cycles)
    _, _, H_now = compute_H(state.cycles)

    surviving: list[Rule] = []
    for rule in state.rules:
        if rule.applied_at_cycle is None:
            surviving.append(rule)
            continue
        elapsed = cycles_now - rule.applied_at_cycle
        if elapsed < OBSERVATION_WINDOW:
            surviving.append(rule)
            continue
        baseline = rule.H_at_apply if rule.H_at_apply is not None else 0.0
        if H_now < baseline - H_DROP_TOLERANCE:
            reverted.append(rule.id)
            state.revert_log.append(
                f"auto-revert rule {rule.pattern!r} ({rule.type}): "
                f"H {baseline:.3f} -> {H_now:.3f}"
            )
            continue
        rule.applied_at_cycle = None
        rule.H_at_apply = None
        surviving.append(rule)
    state.rules = surviving
    return reverted


def maybe_propose(state: State) -> list[Proposal]:
    if len(state.cycles) % PROPOSE_EVERY != 0 or not state.cycles:
        return []
    new = propose_rules(state)
    if new:
        state.proposals.extend(new)
    return new


def record_h_snapshot(state: State) -> None:
    U, Q, H = compute_H(state.cycles)
    state.h_history.append(
        HSnapshot(cycle_index=len(state.cycles), U=U, Q=Q, H=H)
    )
    if len(state.h_history) > 200:
        state.h_history = state.h_history[-200:]
