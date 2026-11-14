# Astro Health Monitor

**NASA Space Apps Challenge 2026 · Reto: Create Health Monitoring Software for Astronauts on Space Missions**
Equipo: _(nombre del equipo)_

> ⚠️ **Prototipo educativo. No es un dispositivo médico ni reemplaza a un profesional de salud.**

## Problema
Los astronautas que viajan lejos de la Tierra tienen atención médica limitada y están expuestos a riesgos como radiación, pérdida ósea y fatiga. Monitorear su estado a diario permite detectar desviaciones a tiempo.

## Solución
Un solo dashboard con dos partes:

1. **Parte 1, predicción:** con sensores reales medimos frecuencia cardíaca, sueño, SpO₂ (si hay pulsioxímetro) y tiempo de reacción. Calculamos una línea base personal, detectamos desviaciones y predecimos el siguiente tiempo de reacción.
2. **Parte 2, descripción:** estadística básica (mínimo, máximo, promedio, desviación) sobre datasets públicos de indicadores difíciles de medir en la ISS.

_(Captura del dashboard: pendiente, `docs/images/`)_

## Qué es real, qué es público y qué es sintético
| Dato | Origen |
|---|---|
| FC, sueño, SpO₂, tiempo de reacción del equipo | **Medido por nosotros** (análogo terrestre, 3 personas anonimizadas A, B, C) |
| Datasets de la Parte 2 y de la Capa 2 del modelo | **Dataset público** (ver Fuentes) |
| Datos de ejemplo en `data/sample/` | **Sintético** (solo para probar la app) |

## Cómo ejecutarlo
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app/streamlit_app.py
```

## Metodología
- **Parte 1:** línea base personal (media y desviación), puntaje z, semáforo verde/amarillo/rojo (|z| < 1,5 / 1,5–2,5 / > 2,5), y predicción del tiempo de reacción con Ridge y GradientBoosting, comparada contra la referencia ingenua "mañana = hoy" (MAE). _(por completar)_
- **Parte 2:** limpieza con pandas y estadísticas por indicador y etapa (antes, durante y después del vuelo). _(por completar)_

## Resultados y limitaciones
- Muestra de **n = 3** personas durante 2 días: es una **prueba de concepto**, no una validación estadística.
- Medimos personas en la Tierra como **análogo** de la ISS.
- No es dispositivo médico ni da diagnósticos.

## Fuentes y licencias
Ver [`data/external/SOURCES.md`](data/external/SOURCES.md).

## Uso de herramientas de IA
_(Declarar aquí los asistentes de IA usados para código o texto.)_

## Integrantes y licencia
_(Nombres o alias de las 3 personas.)_ · Licencia [MIT](LICENSE).
