"""Reads the metrics detected by ia.py, prints a console report
and builds the payload the backend sends to the frontend."""

import math

try:
    from .ia import evaluate_metrics, evaluate_optional, overall_status
except ImportError:
    from ia import evaluate_metrics, evaluate_optional, overall_status

# Last reading per subject (used by /api/chat and /api/home)
_last_readings = {}
_last_reading = None


def _required_number(payload, key):
    value = payload.get(key)
    if value is None or value == "":
        raise ValueError(f"{key} is required")
    try:
        number = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{key} must be numeric") from None
    if not math.isfinite(number):
        raise ValueError(f"{key} must be finite")
    return number


def _fmt(value):
    return int(value) if value == int(value) else value


def read_metrics(payload):
    """Takes the frontend payload, evaluates the metrics with ia.py,
    prints the report and returns the JSON response for the frontend."""
    global _last_reading
    payload = payload or {}

    bpm = _required_number(payload, 'hr_bpm')
    spO2 = _required_number(payload, 'spo2_pct')
    sleep = _required_number(payload, 'sleep_hours')
    reaction = _required_number(payload, 'rt_ms')
    fatigue = _required_number(payload, 'fatigue_level')

    metrics = evaluate_metrics(bpm, spO2, sleep, reaction, fatigue)
    metrics.update(evaluate_optional(payload))
    general = overall_status(metrics)

    reading = {
        'subject_id': payload.get('subject_id', 'A'),
        'metrics': metrics,
        'overall_status': general,
        'ai_response': build_ai_response(metrics, general),
    }
    _last_readings[reading['subject_id']] = reading
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


def get_last_reading(subject_id=None):
    """Last reading of a subject, or the most recent one if no subject
    is given."""
    if subject_id is not None:
        return _last_readings.get(subject_id)
    return _last_reading


if __name__ == '__main__':
    # Quick test without the frontend
    read_metrics({'subject_id': 'A', 'hr_bpm': 72, 'spo2_pct': 96,
                  'sleep_hours': 6.5, 'rt_ms': 420, 'fatigue_level': 6,
                  'blood_glucose': 105, 'bp_systolic': 128, 'bp_diastolic': 82})
