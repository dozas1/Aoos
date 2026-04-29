from __future__ import annotations

from pydantic import BaseModel, Field

SIGNAL_TYPES = ["σ.s", "σ.c", "σ.r", "UNKNOWN"]


class Rule(BaseModel):
    id: str
    pattern: str
    type: str
    source: str = "user"
    hits: int = 0
    correct: int = 0
    applied_at_cycle: int | None = None
    H_at_apply: float | None = None


class Cycle(BaseModel):
    id: str
    text: str
    proposed_type: str
    matched_rule_id: str | None = None
    escalated: bool = False
    user_decision: bool | None = None
    true_type: str | None = None
    timestamp: float


class Proposal(BaseModel):
    id: str
    pattern: str
    type: str
    evidence_cycle_ids: list[str] = Field(default_factory=list)


class HSnapshot(BaseModel):
    cycle_index: int
    U: float
    Q: float
    H: float


class State(BaseModel):
    rules: list[Rule] = Field(default_factory=list)
    cycles: list[Cycle] = Field(default_factory=list)
    proposals: list[Proposal] = Field(default_factory=list)
    h_history: list[HSnapshot] = Field(default_factory=list)
    revert_log: list[str] = Field(default_factory=list)
