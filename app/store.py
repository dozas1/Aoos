from __future__ import annotations

import asyncio
import json
import os
import uuid
from pathlib import Path

from .models import Rule, State

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
STATE_PATH = DATA_DIR / "state.json"

_lock = asyncio.Lock()


def _seed_rules() -> list[Rule]:
    return [
        Rule(
            id=str(uuid.uuid4()),
            pattern=r"(?i)bug|error|crash|fall",
            type="σ.s",
            source="seed",
        ),
        Rule(
            id=str(uuid.uuid4()),
            pattern=r"(?i)\b(haz|crea|implementa|corré|corre|ejecuta)\b",
            type="σ.c",
            source="seed",
        ),
        Rule(
            id=str(uuid.uuid4()),
            pattern=r"(?i)respuesta|listo|done|hecho",
            type="σ.r",
            source="seed",
        ),
    ]


def load() -> State:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not STATE_PATH.exists():
        state = State(rules=_seed_rules())
        _write_sync(state)
        return state
    raw = STATE_PATH.read_text(encoding="utf-8")
    return State.model_validate_json(raw)


def _write_sync(state: State) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    tmp = STATE_PATH.with_suffix(".json.tmp")
    tmp.write_text(state.model_dump_json(indent=2), encoding="utf-8")
    os.replace(tmp, STATE_PATH)


async def save(state: State) -> None:
    async with _lock:
        await asyncio.to_thread(_write_sync, state)
