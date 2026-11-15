"""Reads the metrics detected by ia.py, prints a console report
and builds the payload the backend sends to the frontend."""

try:
    from .ia import evaluate_metrics, evaluate_optional, overall_status
except ImportError:
    from ia import evaluate_metrics, evaluate_optional, overall_status

# Default values for the core metrics when the frontend omits them
DEFAULTS = {
    'hr_bpm': 75,
    'spo2_pct': 98,
    'sleep_hours': 8,
    'rt_ms': 250,
    'fatigue_level': 3,
}

# Last reading received (used by /api/chat)
_last_reading = None


def _number(value, default):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _fmt(value):
    return int(value) if value == int(value) else value


def read_metrics(payload):
    """Takes the frontend payload, evaluates the metrics with ia.py,
    prints the report and returns the JSON response for the frontend."""
    global _last_reading
    payload = payload or {}

    bpm = _number(payload.get('hr_bpm'), DEFAULTS['hr_bpm'])
    spO2 = _number(payload.get('spo2_pct'), DEFAULTS['spo2_pct'])
    sleep = _number(payload.get('sleep_hours'), DEFAULTS['sleep_hours'])
    reaction = _number(payload.get('rt_ms'), DEFAULTS['rt_ms'])
    fatigue = _number(payload.get('fatigue_level'), DEFAULTS['fatigue_level'])

    metrics = evaluate_metrics(bpm, spO2, sleep, reaction, fatigue)
    metrics.update(evaluate_optional(payload))
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
    """Text summary the frontend prints directly."""
    parts = [
        f"{m['label']}: {m['value']}{m['unit']} ({m['status']})"
        for m in metrics.values()
    ]
    return 'Metrics analyzed: ' + ' | '.join(parts) + f'. Overall status: {general}'


def print_report(reading):
    print('\n=== METRICS REPORT ===')
    print(f"Subject: {reading['subject_id']}")
    for m in reading['metrics'].values():
        print(f"  {m['label']}: {m['value']} {m['unit']} -> {m['status']}")
    print(f"  Overall status: {reading['overall_status']}")
    print('=======================\n')


def get_last_reading():
    return _last_reading


if __name__ == '__main__':
    # Quick test without the frontend
    read_metrics({'subject_id': 'A', 'hr_bpm': 72, 'spo2_pct': 96,
                  'sleep_hours': 6.5, 'rt_ms': 420, 'fatigue_level': 6,
                  'blood_glucose': 105, 'bp_systolic': 128, 'bp_diastolic': 82})
