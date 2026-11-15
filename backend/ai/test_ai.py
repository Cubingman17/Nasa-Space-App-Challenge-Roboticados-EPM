"""Test suite for the AI: thresholds, metric reader, API endpoints
and the local LLM (Ollama).

Usage:
    cd backend
    python -m ai.test_ai
"""

import sys

from ai import local_llm
from ai.ia import evaluate_metrics, overall_status
from ai.metrics_reader import read_metrics

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
    print("\n[1] Metric thresholds (ia.py)")
    cases = [
        # bpm,  spo2, sleep, reaction, expected overall
        (45,   80,   4.0,  600, "critical"),   # everything critical
        (55,   92,   6.5,  320, "atention"),    # everything at attention
        (72,   96,   8.0,  250, "normal"),      # everything normal
        (130,  88,   5.5,  400, "bad"),         # everything bad
        (85,   97,   7.5,  280, "normal"),      # normal with qualifiers
        (160,  99,   9.0,  200, "critical"),    # only bpm critical
        (60,   84,   9.0,  200, "critical"),    # only spo2 critical
        (60,   99,   4.0,  200, "critical"),    # only sleep critical
        (60,   99,   9.0,  550, "critical"),    # only reaction critical
    ]
    for bpm, spo2, sleep, reaction, expected in cases:
        metrics = evaluate_metrics(bpm, spo2, sleep, reaction)
        got = overall_status(metrics)
        check(
            f"bpm={bpm} spo2={spo2} sleep={sleep} rt={reaction} -> {expected}",
            got == expected,
            f"got {got}",
        )

    # Individual status checks
    check("bpm 85 -> 'normal: nervous/stressed'",
          evaluate_metrics(85, 96, 8, 250)["bpm"]["status"] == "normal: nervous/stressed")
    check("sleep 7.5 -> 'normal: a little deficient'",
          evaluate_metrics(60, 96, 7.5, 250)["sleep"]["status"] == "normal: a little deficient")
    check("reaction 280 -> 'normal: a little deficient'",
          evaluate_metrics(60, 96, 8, 280)["reaction"]["status"] == "normal: a little deficient")


def test_reader():
    print("\n[2] Metrics reader (metrics_reader.py)")
    # Values as strings, like the frontend sends them
    reading = read_metrics({"subject_id": "B", "hr_bpm": "95", "spo2_pct": "93",
                            "sleep_hours": "5.5", "rt_ms": "380"})
    check("string values are parsed", reading["metrics"]["bpm"]["value"] == 95.0)
    check("overall status is bad", reading["overall_status"] == "bad")
    check("ai_response is in English", "Overall status" in reading["ai_response"])

    # Missing fields fall back to defaults
    reading = read_metrics({})
    check("empty payload uses defaults", reading["overall_status"] == "normal")
    check("default subject is A", reading["subject_id"] == "A")

    # Invalid values fall back to defaults
    reading = read_metrics({"hr_bpm": "abc", "sleep_hours": None})
    check("invalid values use defaults", reading["overall_status"] == "normal")


def test_api():
    print("\n[3] API endpoints (FastAPI)")
    from fastapi.testclient import TestClient
    from main import app
    client = TestClient(app)

    r = client.post("/api/predict", json={
        "subject_id": "A", "hr_bpm": "95", "spo2_pct": "93",
        "sleep_hours": "5.5", "rt_ms": "380",
        "fatigue_level": "3", "env_temp": "21", "notes": "test",
    })
    check("POST /api/predict returns 200", r.status_code == 200)
    check("predict returns overall_status", r.json().get("overall_status") == "bad")
    check("predict returns 4 metrics", len(r.json().get("metrics", {})) == 4)

    r = client.post("/api/chat", json={"prompt": "how am I doing?"})
    check("POST /api/chat returns 200", r.status_code == 200)
    check("chat includes source", "source" in r.json())
    check("chat reply is not empty", len(r.json().get("reply", "")) > 0)


def test_local_llm():
    print("\n[4] Local LLM (Ollama astroai)")
    if not local_llm.is_available():
        print("  SKIP  Ollama is not running")
        return

    # Load test metrics as context
    reading = read_metrics({"subject_id": "A", "hr_bpm": "95", "spo2_pct": "93",
                            "sleep_hours": "5.5", "rt_ms": "380"})
    reply = local_llm.chat("I feel exhausted, how am I doing?", reading["ai_response"])
    check("local LLM returns a reply", len(reply) > 20, f"got: {reply[:80]}")
    print(f"  Reply: {reply[:200]}...")


def main():
    test_thresholds()
    test_reader()
    test_api()
    test_local_llm()
    print(f"\n{'=' * 40}\nRESULTS: {PASS} passed, {FAIL} failed")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
