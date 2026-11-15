"""Lee las métricas detectadas por ia.py, imprime un reporte en consola
y construye el payload que el backend envía al frontend."""

try:
    from .ia import evaluate_metrics, overall_status
except ImportError:
    from ia import evaluate_metrics, overall_status

# Valores por defecto si el frontend no envía una métrica
DEFAULTS = {
    'hr_bpm': 75,
    'spo2_pct': 98,
    'sleep_hours': 8,
    'rt_ms': 250,
}

# Última lectura recibida (para /api/chat)
_last_reading = None


def _number(value, default):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _fmt(value):
    return int(value) if value == int(value) else value


def read_metrics(payload):
    """Recibe el payload del frontend, evalúa las métricas con ia.py,
    imprime el reporte y devuelve la respuesta JSON para el frontend."""
    global _last_reading
    payload = payload or {}

    bpm = _number(payload.get('hr_bpm'), DEFAULTS['hr_bpm'])
    spO2 = _number(payload.get('spo2_pct'), DEFAULTS['spo2_pct'])
    sleep = _number(payload.get('sleep_hours'), DEFAULTS['sleep_hours'])
    reaction = _number(payload.get('rt_ms'), DEFAULTS['rt_ms'])

    metrics = evaluate_metrics(bpm, spO2, sleep, reaction)
    general = overall_status(metrics)

    reading = {
        'subject_id': payload.get('subject_id', 'A'),
        'metrics': metrics,
        'overall_status': general,
        'ai_response': build_ai_response(metrics, general),
    }
    _last_reading = reading

    print_report(reading)
    return reading


def build_ai_response(metrics, general):
    """Resumen en texto que el frontend imprime directamente."""
    parts = [
        f"{m['label']}: {_fmt(m['value'])}{m['unit']} ({m['status']})"
        for m in metrics.values()
    ]
    return 'Métricas analizadas: ' + ' | '.join(parts) + f'. Estado general: {general}'


def print_report(reading):
    print('\n=== REPORTE DE MÉTRICAS ===')
    print(f"Sujeto: {reading['subject_id']}")
    for m in reading['metrics'].values():
        print(f"  {m['label']}: {_fmt(m['value'])} {m['unit']} -> {m['status']}")
    print(f"  Estado general: {reading['overall_status']}")
    print('===========================\n')


def get_last_reading():
    return _last_reading


if __name__ == '__main__':
    # Prueba rápida sin frontend
    read_metrics({'subject_id': 'A', 'hr_bpm': 72, 'spo2_pct': 96,
                  'sleep_hours': 6.5, 'rt_ms': 420})
