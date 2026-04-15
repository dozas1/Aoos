# Claude — Memoria Persistente

## ═══ SIMU-MAPA v100 ═══

4 archivos pilares son la inteligencia. El modelo es intercambiable. La fórmula H = (1-U)×Q gobierna todo y es falseable.

## Fórmula refinada
```
U = escalaciones_últimos_50 / señales_últimos_50  (cobertura)
Q = no_corregidas / totales                        (calidad)  
H = (1 - U) × Q                                   (homeostasis)
```
U sola no basta — un reflejo malo baja U pero el sistema es inútil. Q corrige eso. H = cobertura × calidad. Es 🔥 falseable: si no predice salud real, se cambia.

## Pilares
- `.cursorrules` — Cursor mide H, ejecuta context.md, no decide arquitectura
- `0c0-agent.md` — constitución + epistemología (Shannon, Cardano, lentes, entropía, incompletitud) + fórmula H con umbrales
- `0c0-memory.md` — tabla de H (runner escribe), decisiones ligadas a fallos, arsenal, modelo default Gemma 3
- `0c0-context.md` — plan de 5 fases con gates de H, quién escribe qué, trasplante explícito de v40, micro-peticiones como protocolo

## Lo que la fórmula me hizo refinar en los archivos
- Agregué Q (calidad) — sin ella U era engañable
- Ventana de 50 ciclos — no all-time
- Cada fallo ahora ligado a la decisión que informó
- Modelo default explícito: Gemma 3
- Tabla "quién escribe qué" elimina ambigüedad
- Gates de fase con H específico + "quién decide avanzar: Ω"
- Trasplante de v40 con archivos exactos listados

## Plan: 5 fases con gates
| Fase | Qué | Gate H |
|------|-----|--------|
| F0 | Esqueleto + trasplante + medir H | corre sin crash |
| F1 | Micro-peticiones (2-4 por ciclo) | H > 0.1 × 10 ciclos |
| F2 | Osmosis traductor JSON | H > 0.3 |
| F3 | Evaluación cruzada | H > 0.4 + 50 evaluaciones |
| F4 | Router adaptativo | H > 0.5 |
| F5 | Loop mejora archivos | H > 0.6 + 1 propuesta útil |

## Sobre Ω
Sistemas > features. Autodidacta. Bakabaka. Esposa embarazada. 32GB RAM, 4GB VRAM. Stack costo fijo. No recomendar descanso.

## Aprendizajes clave esta sesión
- La inteligencia vive en archivos, no en modelos
- Sin contexto cualquier IA es tonta (Phi-4 "hola" → ecuación)
- Micro-peticiones: 256 tokens × 4 > 2048 tokens × 1
- Fallar = medir (documentar fallos vale más que éxito silencioso)
- La fórmula debe medir cobertura Y calidad (U sola es engañable)
- Gobernanza = modelar entropía, no indicar qué hacer
- Incompletitud: reducir U revela más entropía. Eso está bien.
- Cada repo (v30, v40) es alimento futuro
- Retroalimentación ES aprendizaje
