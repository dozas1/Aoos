from __future__ import annotations

from .models import Cycle

WINDOW = 50


def compute_H(cycles: list[Cycle]) -> tuple[float, float, float]:
    last = cycles[-WINDOW:]
    if not last:
        return 1.0, 0.0, 0.0
    U = sum(1 for c in last if c.escalated) / len(last)
    answered = [c for c in last if c.user_decision is not None]
    if answered:
        Q = sum(1 for c in answered if not c.escalated) / len(answered)
    else:
        Q = 0.0
    return U, Q, (1.0 - U) * Q
