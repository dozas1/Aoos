# 0c0 — Memoria

## Registro de H (el runner escribe cada 10 ciclos)
```
H = (1 - U) × Q
U = escalaciones_últimos_50 / señales_últimos_50
Q = no_corregidas(últimos_50) / totales(últimos_50)
```
| Ciclo | U | Q | H | Nota |
|-------|---|---|---|------|
| 0 | 1.0 | — | 0.0 | Inicio. Sin reflejos. Todo escala. |
<!-- Runner agrega. Cursor no toca esta tabla. -->

## Decisiones congeladas (❄️)
| ID | Decisión | Viene de |
|----|----------|----------|
| D01 | Inteligencia vive en archivos, no en modelo | Phi-4 "hola" = ecuación |
| D02 | Micro-peticiones > macro | Gemma no puede "analizar todo" |
| D03 | Gemma = techo local, usar con intención (no para trivialidades L0) | Sweet spot validado v40 |
| D04 | DeepSeek R1 descartado local | 9min, superficial, v40 ciclo 29 |
| D05 | Orquestador = código, no modelo | P06 del doc de arquitectura |
| D06 | Cascada L0→L5, no saltar | Propagación controlada |
| D07 | Archivos primero, código después | v30/v40 bottom-up falló |
| D08 | Sin contexto → IA tonta | Phi-4 "hola", toda la sesión |
| D09 | Fallar = medir límites | Cardano, epistemología |
| D10 | Reglas limitan, modelan entropía | Gobernanza = reducir incertidumbre |
| D11 | Cada herramienta → la siguiente | Lentes → microscopio → telescopio |
| D12 | Fórmula H es 🔥 falseable | Si no predice, se cambia |
| D13 | Scope = resolver, no anticipar. Sobre-ingeniería = complejidad sin problema | Resolver abre puertas que antes eran sobre-ingeniería |
| D14 | Comprensión = compresión. Reflejos no son cache, son reglas destiladas | GPS = lentes + tiempo + espacio. Cada herramienta comprime un dominio |

## Lo que funciona (validado)
- OPA como ciclo universal
- JSON puro como respuesta de λ
- Anti-inflación R1-R4
- Cristalización → costo 0 (ver definición en `0c0-agent.md` § Conceptos clave)
- TF-IDF + cosine (búsqueda de reflejos sin dependencias externas)
- Poda automática (reflejos con hit=0 tras N ciclos se eliminan para no inflar SQLite)
- Streaming + monitoreo actividad > timeout (30s sin output = proceso muerto)
- Extracción granular (parsear ### headers como evidencia separada, no texto monolítico)
- Degradación automática (si modelo falla, bajar a siguiente en cascada sin crash)
- Protocolo universal llm.py (interfaz única: cargar/descargar/llamar funciona igual para cualquier modelo)
- Señales Ω (σ.c) bypass reflejos: van directo a λ sin buscar en SQLite

## Fallos documentados (cada fallo informa una decisión)
| Fallo | Qué pasó | Decisión que informa |
|-------|----------|---------------------|
| JSON truncado v30 | max_tokens=512 + thinking~600 | min 1536, ahora 2048 |
| Tareas en cascada v30 | λ generó T-003→T-006 sin completar | R1-R4 anti-inflación |
| Propuesta CAC v40 | P02 disfrazada de protocolo | Rechazar frameworks sin datos |
| DeepSeek R1 local | 9min, respondió sobre sí mismo | D04: descartado local |
| Phi-4 "hola" | 1m34s pensando tarea trivial | D01: contexto > modelo |
| Gemma 4 no carga | Otros modelos en RAM | Descargar todo antes de cargar |
| Timeout 600s | Mata trabajo legítimo en progreso | Streaming + silencio 30s |
| Gemma propone DOC | Premature formalization | Redirigir a capacidades concretas |

## Patrones tóxicos de Ω
Cuando 0c0 detecta un patrón, responde con el antídoto (pregunta de redirección).
| Patrón | Antídoto |
|--------|----------|
| Scope explosion | "¿Cuál es la UNA cosa?" |
| Premature formalization | "¿3 ejemplos concretos?" |
| Planning paralysis | Crear artefacto ya |
| Restart pattern | "¿Qué funciona hoy?" |
| Abstraction sin path | "¿Corre con if/else?" |
| Resource anxiety | "¿Estás en 90% ahora?" |

## Hardware
RAM: 32GB | GPU: RTX 3050, 4GB VRAM | SSD: 500GB | LM Studio: puerto 1234

## Modelo default
Cargar al inicio: **Gemma 3** (estable). Gemma 4 E4B solo si carga sin problemas. Si falla → Gemma 3 siempre funciona. El runner detecta automáticamente qué modelo está cargado.

## Arsenal
| Modelo | Rol | Capa |
|--------|-----|------|
| SmolLM2 135M | Ruido/entrenamiento | L0 |
| Osmosis 0.6B | Traductor JSON | L0 |
| SmolLM2 1.7B | Clasificación | L0 |
| Stable Code 3B | Código | L0 |
| SmolLM3 3B | Tools, español | L0 |
| Phi-4 Mini | Razonamiento (NO trivial) | L0 |
| SQLCoder 7B | SQL | L0 |
| Gemma 3 / 4 | Techo local | L1 |

## Aprendizajes acumulados
<!-- Cursor agrega con: - [fase-ciclo] aprendizaje. Runner agrega con: - [ciclo#] aprendizaje. -->
- [v30] Bottom-up sin propósito = loop vacío
- [v40] Consolidar > proliferar archivos
- [v40] Retroalimentación (feedback loop: resultado → ajuste → nuevo ciclo) ES el aprendizaje
- [v40] Osmosis desbloquea modelos chicos
- [v100] Cada repo anterior es alimento futuro
- [v100] Preguntas correctas > fuerza bruta
- [v100] Cada herramienta habilita la siguiente
- [v100] U nunca llega a 0. Reducir incertidumbre revela más entropía. Eso está bien.
- [v100] Comprensión = compresión: entender la regla elimina memorizar cada estado. Costo → 0.
- [v100] H es brújula (tiempo real), memory es mapa (emitido por exploración). No diseñar el mapa — dejarlo emerger.
