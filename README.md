# Φ-loop

App full-stack mínima que materializa el ciclo `observar → pensar → actuar → ¿sobre-ingeniería? → feedback`. Es un clasificador de señales de texto que **propone modificaciones a sus propias reglas** cuando detecta patrones en sus errores y revierte automáticamente las que bajan H.

## La fórmula

```
U = escalaciones / total          (cobertura inversa, ventana 50)
Q = aciertos / decididos          (calidad)
H = (1 − U) × Q                   (homeostasis)
```

Una clasificación es **escalada** si ninguna regla matcheó o si el usuario corrigió el tipo propuesto.

## Cómo corre

```bash
pip install -r requirements.txt
pytest tests/                                     # 13 tests
uvicorn app.main:app --reload --port 8000
# abrir http://localhost:8000
```

## Flujo end-to-end

1. Pegá una señal en el input (`"hay un bug en login"`).
2. La app la clasifica con la primera regla que matchea (ordenadas por precisión).
3. Aceptás (✓) o corregís (✗ + tipo correcto).
4. Cada 10 ciclos: si hay ≥3 escalaciones del mismo tipo con un token común y selectivo, aparece una **propuesta** de regla nueva.
5. Aplicás la propuesta — entra en período de observación (10 ciclos).
6. Si H se mantiene → la regla se gradúa. Si H cae >0.05 → se revierte sola.

## Layout

```
app/        backend (FastAPI)
  models.py   Pydantic
  metrics.py  compute_H
  store.py    JSON atómico
  flow.py     classify + propose + auto-revert
  main.py     rutas
static/     index.html (UI vanilla, polling 2s)
data/       state.json (autogenerado)
tests/      pytest
```

## Endpoints

- `GET /api/state` — H, U, Q, ciclos recientes, reglas, propuestas, sparkline.
- `POST /api/signal` — `{text}` → clasifica.
- `POST /api/signal/{id}/decide` — `{accepted, true_type?}` → feedback.
- `POST /api/proposals/{id}/apply` — promueve propuesta a regla en observación.
- `DELETE /api/proposals/{id}` — descarta propuesta.
- `DELETE /api/rules/{id}` — borra regla manualmente.

## Reseteo

`rm data/state.json` y reiniciá el server. Vuelve a las 3 reglas seed.
