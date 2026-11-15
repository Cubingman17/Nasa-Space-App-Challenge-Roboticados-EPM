"""Test suite for the AI: thresholds, metric reader, API endpoints
and the local LLM (Ollama).

Usage:
    cd backend
    python -m ai.test_ai
"""

import sys

from ai import local_llm
from ai.ia import (
    blood_pressure_value,
    body_temp_value,
    co2_value,
    evaluate_metrics,
    evaluate_optional,
    fatigue_value,
    glucose_value,
    mood_value,
    overall_status,
    radiation_value,
)
from ai.metrics_reader import get_last_reading, read_metrics

PASS = 0
FAIL = 0


def check(name, condition, detail=""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  PASS  {name}")
    else:
        FAIL += 1
        print(f"  FAIL  {name}  {detail}")


def test_thresholds():
    print("\n[1] Core metric thresholds (ia.py)")
    cases = [
        # bpm, spo2, sleep, reaction, fatigue, expected overall
        (45,   80,   4.0,  600, 9, "critical"),
        (55,   92,   6.5,  320, 4, "atention"),
        (72,   96,   8.0,  250, 2, "normal"),
        (130,  88,   5.5,  400, 6, "bad"),
        (85,   97,   7.5,  280, 3, "normal"),
        (160,  99,   9.0,  200, 1, "critical"),
        (60,   84,   9.0,  200, 1, "critical"),
        (60,   99,   4.0,  200, 1, "critical"),
        (60,   99,   9.0,  550, 1, "critical"),
        (60,   99,   9.0,  200, 8, "critical"),   # only fatigue critical
    ]
    for bpm, spo2, sleep, reaction, fatigue, expected in cases:
        metrics = evaluate_metrics(bpm, spo2, sleep, reaction, fatigue)
        got = overall_status(metrics)
        check(
            f"bpm={bpm} spo2={spo2} sleep={sleep} rt={reaction} fat={fatigue} -> {expected}",
            got == expected,
            f"got {got}",
        )

    check("bpm 85 -> 'normal: nervous/stressed'",
          evaluate_metrics(85, 96, 8, 250, 2)["bpm"]["status"] == "normal: nervous/stressed")
    check("sleep 7.5 -> 'normal: a little deficient'",
          evaluate_metrics(60, 96, 7.5, 250, 2)["sleep"]["status"] == "normal: a little deficient")
    check("reaction 280 -> 'normal: a little deficient'",
          evaluate_metrics(60, 96, 8, 280, 2)["reaction"]["status"] == "normal: a little deficient")


def test_optional_thresholds():
    print("\n[2] Optional metric thresholds (ia.py)")
    check("glucose 65 -> critical", glucose_value(65) == "critical")
    check("glucose 90 -> normal", glucose_value(90) == "normal")
    check("glucose 110 -> atention", glucose_value(110) == "atention")
    check("glucose 150 -> bad", glucose_value(150) == "bad")
    check("glucose 220 -> critical", glucose_value(220) == "critical")

    check("bp 118/78 -> normal", blood_pressure_value(118, 78) == "normal")
    check("bp 130/85 -> atention", blood_pressure_value(130, 85) == "atention")
    check("bp 85/55 -> atention (hypotension)", blood_pressure_value(85, 55) == "atention")
    check("bp 145/92 -> bad", blood_pressure_value(145, 92) == "bad")
    check("bp 170/105 -> critical", blood_pressure_value(170, 105) == "critical")

    check("temp 36.5 -> normal", body_temp_value(36.5) == "normal")
    check("temp 35.5 -> atention", body_temp_value(35.5) == "atention")
    check("temp 38.5 -> bad", body_temp_value(38.5) == "bad")
    check("temp 39.5 -> critical", body_temp_value(39.5) == "critical")
    check("temp 34.5 -> critical", body_temp_value(34.5) == "critical")

    check("mood 8 -> normal", mood_value(8) == "normal")
    check("mood 5 -> atention", mood_value(5) == "atention")
    check("mood 3 -> bad", mood_value(3) == "bad")
    check("mood 2 -> critical", mood_value(2) == "critical")

    check("radiation 300 -> normal", radiation_value(300) == "normal")
    check("radiation 800 -> atention", radiation_value(800) == "atention")
    check("radiation 1500 -> bad", radiation_value(1500) == "bad")
    check("radiation 3000 -> critical", radiation_value(3000) == "critical")

    check("co2 800 -> normal", co2_value(800) == "normal")
    check("co2 2000 -> atention", co2_value(2000) == "atention")
    check("co2 3500 -> bad", co2_value(3500) == "bad")
    check("co2 6000 -> critical", co2_value(6000) == "critical")

    check("fatigue 2 -> normal", fatigue_value(2) == "normal")
    check("fatigue 5 -> atention", fatigue_value(5) == "atention")
    check("fatigue 7 -> bad", fatigue_value(7) == "bad")
    check("fatigue 9 -> critical", fatigue_value(9) == "critical")


def test_reader():
    print("\n[3] Metrics reader (metrics_reader.py)")
    # Values as strings, like the frontend sends them
    reading = read_metrics({"subject_id": "B", "hr_bpm": "95", "spo2_pct": "93",
                            "sleep_hours": "5.5", "rt_ms": "380", "fatigue_level": "6",
                            "blood_glucose": "110", "bp_systolic": "130", "bp_diastolic": "85"})
    check("string values are parsed", reading["metrics"]["bpm"]["value"] == 95.0)
    check("overall status is bad", reading["overall_status"] == "bad")
    check("ai_response is in English", "Overall status" in reading["ai_response"])
    check("optional glucose included", "glucose" in reading["metrics"])
    check("optional blood pressure included", "blood_pressure" in reading["metrics"])
    check("blood pressure value formatted", reading["metrics"]["blood_pressure"]["value"] == "130/85")

    # Missing optional fields are simply absent when all core metrics exist
    reading = read_metrics({"hr_bpm": "70", "spo2_pct": "98",
                            "sleep_hours": "8", "rt_ms": "250",
                            "fatigue_level": "2"})
    check("optionals absent when not sent", "glucose" not in reading["metrics"])

    # Missing core fields are rejected instead of replaced with invented values
    rejected_empty_payload = False
    try:
        read_metrics({})
    except ValueError:
        rejected_empty_payload = True
    check("empty payload is rejected", rejected_empty_payload)

    reading = read_metrics({"hr_bpm": "70", "spo2_pct": "98",
                            "sleep_hours": "8", "rt_ms": "250",
                            "fatigue_level": "2"})
    check("default subject is A", reading["subject_id"] == "A")

    # Each subject keeps their own last reading
    read_metrics({"subject_id": "A", "hr_bpm": "70", "spo2_pct": "98",
                  "sleep_hours": "8", "rt_ms": "250", "fatigue_level": "2"})
    read_metrics({"subject_id": "B", "hr_bpm": "130", "spo2_pct": "88",
                  "sleep_hours": "4", "rt_ms": "600", "fatigue_level": "9"})
    check("subject A keeps their own reading",
          get_last_reading("A")["overall_status"] == "normal")
    check("subject B keeps their own reading",
          get_last_reading("B")["overall_status"] == "critical")
    check("latest reading without subject", get_last_reading()["subject_id"] == "B")
    check("unknown subject has no reading", get_last_reading("Z") is None)

    # Invalid values are rejected instead of replaced with invented values
    rejected_invalid_payload = False
    try:
        read_metrics({"hr_bpm": "abc", "sleep_hours": None})
    except ValueError:
        rejected_invalid_payload = True
    check("invalid values are rejected", rejected_invalid_payload)


def test_api():
    print("\n[4] API endpoints (FastAPI)")
    from fastapi.testclient import TestClient
    from main import app
    from database import init_db
    init_db()
    client = TestClient(app)

    r = client.post("/api/predict", json={
        "subject_id": "A", "hr_bpm": "95", "spo2_pct": "93",
        "sleep_hours": "5.5", "rt_ms": "380", "fatigue_level": "6",
        "blood_glucose": "110", "bp_systolic": "130", "bp_diastolic": "85",
        "body_temp_c": "37.8", "mood_level": "4", "radiation_usv": "800",
        "cabin_co2": "2000", "env_temp": "21", "notes": "test",
    })
    check("POST /api/predict returns 200", r.status_code == 200)
    check("predict returns overall_status", r.json().get("overall_status") == "bad")
    check("predict returns 5 core metrics",
          all(k in r.json().get("metrics", {}) for k in ["bpm", "spO2", "sleep", "reaction", "fatigue"]))
    check("predict returns optional metrics",
          all(k in r.json().get("metrics", {}) for k in ["glucose", "blood_pressure", "body_temp", "mood", "radiation", "cabin_co2"]))

    r = client.post("/api/chat", json={"prompt": "how am I doing?"})
    check("POST /api/chat returns 200", r.status_code == 200)
    check("chat includes source", "source" in r.json())
    check("chat reply is not empty", len(r.json().get("reply", "")) > 0)


def test_local_llm():
    print("\n[5] Local LLM (Ollama astroai)")
    if not local_llm.is_available():
        print("  SKIP  Ollama is not running")
        return

    # Load test metrics as context
    reading = read_metrics({"subject_id": "A", "hr_bpm": "95", "spo2_pct": "93",
                            "sleep_hours": "5.5", "rt_ms": "380", "fatigue_level": "6",
                            "blood_glucose": "110", "bp_systolic": "130", "bp_diastolic": "85"})
    reply = local_llm.chat("I feel exhausted, how am I doing?", reading["ai_response"])
    check("local LLM returns a reply", len(reply) > 20, f"got: {reply[:80]}")
    print(f"  Reply: {reply[:200]}...")


def main():
    test_thresholds()
    test_optional_thresholds()
    test_reader()
    test_api()
    test_local_llm()
    print(f"\n{'=' * 40}\nRESULTS: {PASS} passed, {FAIL} failed")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
