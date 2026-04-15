# 0c0 — Contexto y Plan de Construcción

## Φ aplicada a cada nivel
```
Φ es la misma en todos los niveles. Solo cambia S:

Ω+Claude    → Φ(pilares)    → refinar archivos         → H_archivos sube
Cursor (Ψ)  → Φ(código)     → construir/corregir       → H_sistema sube
Runner      → Φ(señales)    → micro-peticiones a λ      → H_operativo sube
                    ↑                                          |
                    └──── memory se emite como subproducto ────┘
```
Φ completa y H definidas en `0c0-agent.md`. El runner registra H cada 10 ciclos en `0c0-memory-1.md`. Cursor reporta H antes/después. Ω decide transiciones.

## Quién escribe qué
| Archivo | Runner escribe | Cursor escribe | Ω/Claude escribe |
|---------|---------------|----------------|------------------|
| cursorrules.md | — | — | Todo |
| 0c0-agent.md | — | — | Todo |
| 0c0-memory-1.md | Tabla H, Aprendizajes | Fallos, Aprendizajes | Decisiones, Leyes |
| 0c0-context.md | — | Checkboxes de tareas | Fases, Gates, Plan |
| state.json | Todo | Lee | Lee |
| claude-memory.md | — | — | Claude escribe (memoria entre sesiones, no es pilar) |
| db/0v0.db | Todo | Lee | — |

**state.json**: estado volátil del runner. Contiene: `ciclo_actual`, `fase`, `modelo_activo`, `U`, `Q`, `H`, `timestamp`. El runner lo escribe cada ciclo. No es fuente de verdad — la fuente es `0c0-memory-1.md`.

## Micro-peticiones — Φ(señal)
```
Señal entra al runner → Φ busca δ_min para resolverla:
  1. "Clasifica: {señal}" → {tipo, prioridad}       128 tokens
  2. Buscar reflejo en SQLite (gap = ¿ya sé esto?)
  3. Si reflejo → usar (U no sube, costo 0). Si no:
  4. "Responde: {señal}" → {respuesta}               256 tokens
  5. "Extrae tags: {respuesta}" → {tags}              64 tokens
  6. Cristalizar como reflejo → U baja en futuros ciclos
```
2-4 llamadas por señal. Cada una es δ_min — la pregunta más chica posible.

## Cascada — Φ(modelo)
```
Φ prueba el recurso más barato primero (δ_min en costo):
  Reflejo local → costo 0 (comprensión cristalizada)
    ↓ no hay
  L0 (<3B) → micro-tarea rápida
    ↓ no resuelve
  L1 (Gemma) → razonamiento local
    ↓ no resuelve
  L2→L5 → remoto (futuro)
```

## ═══ PLAN DE CONSTRUCCIÓN — Φ(sistema) a escala macro ═══
Cada fase es un δ. Los gates son H(S') > umbral. Ω decide persist/next.

### FASE 0: Esqueleto
Estado: 🔥 ACTIVA

```
v100-0v0/
├── cursorrules.md
├── 0c0-agent.md
├── 0c0-memory-1.md
├── 0c0-context.md
├── core/
│   ├── llm.py
│   ├── memoria.py
│   └── router.py
├── runner/
│   └── main.py
├── db/
├── logs/
├── inbox/
└── propuestas/
```

Tareas:
- [ ] Crear estructura de carpetas
- [ ] Colocar los 4 archivos pilares en raíz
- [ ] Trasplantar de v40 (archivos exactos):
  - Solicitar ruta de v40 a Ω (repos anteriores se proveen on-demand cuando 0c0 las pide)
  - v40 es material de construcción, no reliquia (D15). Copiar y adaptar, no preservar.
  - `core/llm.py` → copiar entero (streaming, modelo_activo, cargar, descargar)
  - `core/memoria.py` → copiar entero (SQLite, buscar TF-IDF, guardar, hit, degradar)
  - `core/router.py` → copiar SOLO clasificar_señal() y búsqueda de reflejos. NO el router multimodelo.
- [ ] Crear `runner/main.py` NUEVO (no copiar de v40) que:
  - Siga OPA
  - Use micro-peticiones (2-4 por ciclo)
  - Calcule H cada 10 ciclos y escriba en 0c0-memory-1.md
  - Display: `[H] 0.00 (U=1.00 Q=—) | Ciclo #1 | Gemma 3`
  - Lea inbox/ para señales de Ω (un .txt por señal, el runner lee y borra al procesar)
  - Sin señal → señal interna SIMPLE: "Revisa estado"
  - max_tokens=256 por micro-petición
  - Streaming con monitoreo de actividad (30s sin output = cancelar esa petición, loguear, seguir con la siguiente)
  - psutil para hardware awareness (RAM libre antes de llamar a λ; si <4GB, loguear warning)
  - NUNCA crashea (try/except en el loop principal: loguear error, continuar al siguiente ciclo)
- [ ] Verificar: 1 ciclo completo, H se reporta, sin crash

Gate: no hay gate de H para Fase 0. Solo "corre sin crash y mide H".

### FASE 1: Micro-peticiones funcionando
Estado: pendiente → Ω activa cuando Fase 0 pasa

- [ ] El runner hace 2-4 micro-peticiones por ciclo (no 1 macro)
- [ ] Cada respuesta útil → guardar como reflejo con tags
- [ ] Los reflejos empiezan a resolver señales sin escalar
- [ ] H empieza a subir desde 0

Gate: **H > 0.1** durante 10 ciclos consecutivos (el sistema cristaliza algo útil)
Quién decide avanzar: Ω

### FASE 2: Osmosis como traductor JSON
Estado: pendiente

- [ ] Modelos L0 responden texto → swap → Osmosis estructura JSON → runner parsea
- [ ] Gemma sigue respondiendo JSON directo
- [ ] Más modelos pueden participar en el loop

Gate: **H > 0.3** (cobertura+calidad mejoran con más modelos participando)
Quién decide avanzar: Ω

### FASE 3: Evaluación cruzada
Estado: pendiente

- [ ] Modelo chico responde → Gemma evalúa (score 0-5)
- [ ] Perfiles por modelo con datos reales
- [ ] Q sube porque se filtran respuestas malas

Gate: **H > 0.4** y datos de al menos 50 evaluaciones
Quién decide avanzar: Ω

### FASE 4: Router adaptativo
Estado: pendiente

- [ ] Router usa scores acumulados en vez de tabla estática
- [ ] >60% resuelto en L0 sin tocar Gemma

Gate: **H > 0.5**
Quién decide avanzar: Ω

### FASE 5: El loop mejora sus archivos
Estado: pendiente

- [ ] El loop detecta patrones → escribe en propuestas/
- [ ] Propuestas para 0c0-memory-1.md y 0c0-context.md
- [ ] Ω/Claude revisan

Gate: **H > 0.6** y al menos 1 propuesta útil implementada
Quién decide avanzar: Ω

## ═══ SIGUIENTE PASO ═══
→ Cursor: ejecuta FASE 0. Crea estructura, coloca pilares, trasplanta de v40 los archivos listados, crea runner nuevo con micro-peticiones y medición de H. Corre 1 ciclo. Reporta.
