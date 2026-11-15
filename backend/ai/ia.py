"""Astronaut health metric detection.

Each function receives a metric value and returns its status:
'critical' > 'bad' > 'atention' > 'normal'

Core metrics (required): BPM, SpO2, sleep, reaction (PVT), fatigue.
Optional metrics: blood glucose, blood pressure, body temperature,
mood, radiation dose, cabin CO2.
"""


def bpm_value(bpm):
    bpm_status = ''
    if bpm < 50:
        bpm_status = 'critical'

    elif bpm >= 50 and bpm < 60:
        bpm_status = 'atention'

    elif bpm >= 60 and bpm <= 100:
        if bpm < 80:
            bpm_status = 'normal'
        else:
            bpm_status = 'normal: nervous/stressed'

    elif bpm > 100 and bpm <= 120:
        bpm_status = 'atention'

    elif bpm > 120 and bpm <= 150:
        bpm_status = 'bad'

    elif bpm > 150:
        bpm_status = 'critical'

    return bpm_status


def spO2_value(spO2):
    spO2_status = ''
    if spO2 >= 95:
        spO2_status = 'normal'

    elif spO2 < 95 and spO2 >= 90:
        spO2_status = 'atention'

    elif spO2 < 90 and spO2 >= 85:
        spO2_status = 'bad'

    elif spO2 < 85:
        spO2_status = 'critical'

    return spO2_status


def sleep_value(sleep):
    sleep_status = ''
    if sleep >= 8:
        sleep_status = 'normal'

    elif sleep >= 7 and sleep < 8:
        sleep_status = 'normal: a little deficient'

    elif sleep >= 6 and sleep < 7:
        sleep_status = 'atention'

    elif sleep >= 5 and sleep < 6:
        sleep_status = 'bad'

    elif sleep < 5:
        sleep_status = 'critical'

    return sleep_status


def reaction_value(reaction):
    reaction_status = ''
    if reaction <= 250:
        reaction_status = 'normal'

    elif reaction > 250 and reaction <= 300:
        reaction_status = 'normal: a little deficient'

    elif reaction > 300 and reaction <= 350:
        reaction_status = 'atention'

    elif reaction > 350 and reaction <= 500:
        reaction_status = 'bad'

    elif reaction > 500:
        reaction_status = 'critical'

    return reaction_status


def fatigue_value(fatigue):
    """Self-reported fatigue level, 1 (fresh) to 10 (exhausted)."""
    if fatigue <= 3:
        return 'normal'

    elif fatigue <= 5:
        return 'atention'

    elif fatigue <= 7:
        return 'bad'

    return 'critical'


def glucose_value(glucose):
    """Blood glucose in mg/dL."""
    if glucose < 70:
        return 'critical'

    elif glucose < 100:
        return 'normal'

    elif glucose < 126:
        return 'atention'

    elif glucose <= 180:
        return 'bad'

    return 'critical'


def blood_pressure_value(systolic, diastolic):
    """Blood pressure in mmHg (systolic/diastolic)."""
    if systolic >= 160 or diastolic >= 100:
        return 'critical'

    elif systolic >= 140 or diastolic >= 90:
        return 'bad'

    elif systolic > 120 or diastolic > 80:
        return 'atention'

    elif systolic < 90 or diastolic < 60:
        return 'atention'

    return 'normal'


def body_temp_value(temp):
    """Body temperature in Celsius."""
    if temp < 35.0:
        return 'critical'

    elif temp < 36.1:
        return 'atention'

    elif temp <= 37.5:
        return 'normal'

    elif temp <= 38.0:
        return 'atention'

    elif temp <= 39.0:
        return 'bad'

    return 'critical'


def mood_value(mood):
    """Self-reported mood, 1 (very low) to 10 (great)."""
    if mood >= 7:
        return 'normal'

    elif mood >= 5:
        return 'atention'

    elif mood >= 3:
        return 'bad'

    return 'critical'


def radiation_value(dose):
    """Radiation dose of the day in microsieverts."""
    if dose < 500:
        return 'normal'

    elif dose <= 1000:
        return 'atention'

    elif dose <= 2000:
        return 'bad'

    return 'critical'


def co2_value(co2):
    """Cabin CO2 concentration in ppm."""
    if co2 < 1000:
        return 'normal'

    elif co2 <= 2500:
        return 'atention'

    elif co2 <= 5000:
        return 'bad'

    return 'critical'


def evaluate_metrics(bpm, spO2, sleep, reaction, fatigue):
    """Evaluates the five core metrics and returns a dictionary with
    value, unit and status of each one."""
    return {
        'bpm': {
            'label': 'BPM',
            'value': bpm,
            'unit': 'bpm',
            'status': bpm_value(bpm),
        },
        'spO2': {
            'label': 'spO2',
            'value': spO2,
            'unit': '%',
            'status': spO2_value(spO2),
        },
        'sleep': {
            'label': 'Sleep',
            'value': sleep,
            'unit': 'h',
            'status': sleep_value(sleep),
        },
        'reaction': {
            'label': 'Reaction',
            'value': reaction,
            'unit': 'ms',
            'status': reaction_value(reaction),
        },
        'fatigue': {
            'label': 'Fatigue',
            'value': fatigue,
            'unit': '/10',
            'status': fatigue_value(fatigue),
        },
    }


def evaluate_optional(payload):
    """Evaluates the optional metrics present in the payload.
    Only the metrics actually sent are included in the result."""
    extras = {}

    glucose = _get_number(payload.get('blood_glucose'))
    if glucose is not None:
        extras['glucose'] = {
            'label': 'Glucose',
            'value': glucose,
            'unit': 'mg/dL',
            'status': glucose_value(glucose),
        }

    systolic = _get_number(payload.get('bp_systolic'))
    diastolic = _get_number(payload.get('bp_diastolic'))
    if systolic is not None and diastolic is not None:
        extras['blood_pressure'] = {
            'label': 'Blood Pressure',
            'value': f'{_fmt(systolic)}/{_fmt(diastolic)}',
            'unit': 'mmHg',
            'status': blood_pressure_value(systolic, diastolic),
        }

    temp = _get_number(payload.get('body_temp_c'))
    if temp is not None:
        extras['body_temp'] = {
            'label': 'Body Temp',
            'value': temp,
            'unit': '°C',
            'status': body_temp_value(temp),
        }

    mood = _get_number(payload.get('mood_level'))
    if mood is not None:
        extras['mood'] = {
            'label': 'Mood',
            'value': mood,
            'unit': '/10',
            'status': mood_value(mood),
        }

    dose = _get_number(payload.get('radiation_usv'))
    if dose is not None:
        extras['radiation'] = {
            'label': 'Radiation',
            'value': dose,
            'unit': 'µSv',
            'status': radiation_value(dose),
        }

    co2 = _get_number(payload.get('cabin_co2'))
    if co2 is not None:
        extras['cabin_co2'] = {
            'label': 'Cabin CO2',
            'value': co2,
            'unit': 'ppm',
            'status': co2_value(co2),
        }

    return extras


def _get_number(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _fmt(value):
    return int(value) if value == int(value) else value


SEVERITY = {'normal': 0, 'atention': 1, 'bad': 2, 'critical': 3}


def _severity(status):
    # 'normal: nervous/stressed' counts as 'normal'
    return SEVERITY.get(status.split(':')[0].strip(), 0)


def overall_status(metrics):
    """Returns the overall status: the most severe metric of the set."""
    worst = 'normal'
    for metric in metrics.values():
        if _severity(metric['status']) > _severity(worst):
            worst = metric['status'].split(':')[0].strip()
    return worst


if __name__ == '__main__':
    bpm = int(input('BPM average: '))
    spO2 = int(input('Actual spO2: '))
    sleep = float(input('Sleep hours: '))
    reaction = int(input('Reaction time (ms): '))
    fatigue = int(input('Fatigue level (1-10): '))

    metrics = evaluate_metrics(bpm, spO2, sleep, reaction, fatigue)
    for metric in metrics.values():
        print(f"{metric['label']}: {metric['value']} {metric['unit']} -> {metric['status']}")
    print(f"Overall: {overall_status(metrics)}")
