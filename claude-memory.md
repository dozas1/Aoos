# Claude — Memoria Persistente

## ═══ SIMU-MAPA v100 ═══

4 archivos pilares son la inteligencia. El modelo es intercambiable. La fórmula H = (1-U)×Q gobierna todo y es falseable.

## Fórmula refinada
```
U = escalaciones_últimos_50 / señales_últimos_50  (cobertura)
Q = no_corregidas(últimos_50) / totales(últimos_50)  (calidad, windowed)
H = (1 - U) × Q                                   (homeostasis)
```
U y Q usan la misma ventana de 50 ciclos para reaccionar rápido a cambios. Es 🔥 falseable: si no predice salud real, se cambia.

## Pilares
- `cursorrules.md` — Cursor mide H, ejecuta 0c0-context.md, no decide arquitectura
- `0c0-agent.md` — constitución + epistemología (Shannon, Cardano, lentes, entropía, incompletitud) + fórmula H con umbrales
- `0c0-memory-1.md` — tabla de H (runner escribe), decisiones ligadas a fallos, arsenal, modelo default Gemma 3
- `0c0-context.md` — plan de 5 fases con gates de H, quién escribe qué, trasplante explícito de v40, micro-peticiones como protocolo

## Lo que el loop recursivo refinó (23 iteraciones, H 0.54→0.98)
- Q windowed a últimos_50 (simétrica con U) — gap en la fórmula original
- OPA unificado a O→P→A→C en todos los archivos
- Todas las referencias de archivo corregidas a nombres reales
- Conceptos core definidos: reflejo, cristalización, 0c0/Ψ relación, σ subtipos, ❄️/🔥/👻
- Lista canónica de los 4 pilares en agent.md
- claude-memory.md + state.json + db/ marcados como soporte (no pilares)
- v40 documentado como recurso on-demand (Ω provee cuando 0c0 pide)
- Items terse de memory expandidos con contexto operativo
- R1-R4 protección explicitada en cursorrules.md
- F4 desambiguado (context window, no archivo)

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
