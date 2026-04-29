from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import flow, store
from .metrics import compute_H
from .models import SIGNAL_TYPES, State

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="Φ-loop", version="0.1.0")

_state: State = store.load()


class SignalIn(BaseModel):
    text: str


class DecisionIn(BaseModel):
    accepted: bool
    true_type: str | None = None


def _serialize_state() -> dict:
    U, Q, H = compute_H(_state.cycles)
    return {
        "U": U,
        "Q": Q,
        "H": H,
        "cycles_count": len(_state.cycles),
        "recent_cycles": [c.model_dump() for c in _state.cycles[-10:]][::-1],
        "h_history": [s.model_dump() for s in _state.h_history[-30:]],
        "rules": [r.model_dump() for r in _state.rules],
        "proposals": [p.model_dump() for p in _state.proposals],
        "revert_log": _state.revert_log[-10:],
        "signal_types": SIGNAL_TYPES,
    }


@app.get("/api/state")
async def get_state():
    return _serialize_state()


@app.post("/api/signal")
async def post_signal(payload: SignalIn):
    text = payload.text.strip()
    if not text:
        raise HTTPException(400, "text vacío")
    cycle = flow.open_cycle(text, _state.rules)
    _state.cycles.append(cycle)
    await store.save(_state)
    return {
        "cycle_id": cycle.id,
        "proposed_type": cycle.proposed_type,
        "matched_rule_id": cycle.matched_rule_id,
        "escalated": cycle.escalated,
    }


@app.post("/api/signal/{cycle_id}/decide")
async def post_decision(cycle_id: str, payload: DecisionIn):
    if not payload.accepted:
        if payload.true_type is None or payload.true_type not in SIGNAL_TYPES:
            raise HTTPException(400, f"true_type debe ser uno de {SIGNAL_TYPES}")
        if payload.true_type == "UNKNOWN":
            raise HTTPException(400, "true_type no puede ser UNKNOWN")
    try:
        flow.apply_decision(_state, cycle_id, payload.accepted, payload.true_type)
    except KeyError:
        raise HTTPException(404, "ciclo no encontrado")

    flow.record_h_snapshot(_state)
    flow.auto_revert_pass(_state)
    flow.maybe_propose(_state)

    await store.save(_state)
    return _serialize_state()


@app.post("/api/proposals/{proposal_id}/apply")
async def apply_proposal(proposal_id: str):
    try:
        rule = flow.apply_proposal(_state, proposal_id)
    except KeyError:
        raise HTTPException(404, "propuesta no encontrada")
    await store.save(_state)
    return {"applied_rule_id": rule.id, "state": _serialize_state()}


@app.delete("/api/proposals/{proposal_id}")
async def delete_proposal(proposal_id: str):
    flow.discard_proposal(_state, proposal_id)
    await store.save(_state)
    return _serialize_state()


@app.delete("/api/rules/{rule_id}")
async def delete_rule(rule_id: str):
    flow.remove_rule(_state, rule_id)
    await store.save(_state)
    return _serialize_state()


app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
async def index():
    return FileResponse(STATIC_DIR / "index.html")
