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


# Actionable suggestions per metric and severity. Shown on the HOME
# banner so the astronaut knows how to improve each yellow/red metric.
SUGGESTIONS = {
    'bpm': {
        'atention': 'Heart rate outside the ideal band: slow down, breathe deeply and rest for 10 minutes.',
        'bad': 'Heart rate is concerning: stop physical effort, hydrate and recheck in 15 minutes.',
        'critical': 'Heart rate is critical: alert the crew medical officer immediately.',
    },
    'spO2': {
        'atention': 'Oxygen saturation is slightly low: check cabin O2 levels and take deep breaths.',
        'bad': 'Oxygen saturation is low: move to a ventilated area and avoid exertion.',
        'critical': 'Oxygen saturation is critical: use supplemental oxygen and alert the crew now.',
    },
    'sleep': {
        'atention': 'Sleep is deficient: protect at least 7 hours tonight and keep a fixed schedule.',
        'bad': 'Serious sleep deficit: schedule a recovery nap before any demanding task.',
        'critical': 'Severe sleep deprivation: stand down from duty and get rest now.',
    },
    'reaction': {
        'atention': 'Reaction time is slowing: avoid high-risk tasks and take a 20-minute nap.',
        'bad': 'Reaction time shows strong fatigue: postpone critical operations.',
        'critical': 'Reaction time is unsafe: do not operate equipment; rest immediately.',
    },
    'fatigue': {
        'atention': 'Fatigue is building: take scheduled breaks, hydrate and snack on protein.',
        'bad': 'High fatigue: delegate tasks and prioritize recovery sleep.',
        'critical': 'Extreme fatigue: stop all non-essential activity and rest.',
    },
    'glucose': {
        'atention': 'Glucose slightly out of range: prefer low-glycemic foods and avoid sugary drinks.',
        'bad': 'Glucose is off-range: eat a balanced meal and recheck before exercise.',
        'critical': 'Glucose is critical: seek medical attention now.',
    },
    'blood_pressure': {
        'atention': 'Blood pressure is borderline: reduce salt, hydrate and rest.',
        'bad': 'Blood pressure is off-range: avoid exertion and recheck in 15 minutes.',
        'critical': 'Blood pressure is critical: alert the crew medical officer.',
    },
    'body_temp': {
        'atention': 'Body temperature is off-range: check thermal comfort of your suit and hydrate.',
        'bad': 'Fever-level temperature: rest, hydrate and monitor hourly.',
        'critical': 'Temperature is critical: seek medical attention now.',
    },
    'mood': {
        'atention': 'Mood is declining: schedule a call with family or crew social time.',
        'bad': 'Mood is low: take a break, exercise or talk with a crewmate.',
        'critical': 'Mood is critically low: reach out to the crew and mission support today.',
    },
    'radiation': {
        'atention': 'Radiation dose is elevated: stay inside shielded modules when possible.',
        'bad': 'Radiation dose is high: limit EVA time and stay in shielded areas.',
        'critical': 'Radiation dose is critical: move to the best-shielded module now.',
    },
    'cabin_co2': {
        'atention': 'Cabin CO2 is rising: check scrubbers and increase ventilation.',
        'bad': 'Cabin CO2 is high: ventilate the module and check the life-support system.',
        'critical': 'Cabin CO2 is dangerous: switch to backup life support immediately.',
    },
}


def build_suggestions(metrics):
    """One suggestion per metric that is not in a normal state."""
    tips = []
    for key, metric in metrics.items():
        base = metric['status'].split(':')[0].strip()
        tip = SUGGESTIONS.get(key, {}).get(base)
        if tip:
            tips.append(tip)
    return tips


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
        'suggestions': build_suggestions(metrics),
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
