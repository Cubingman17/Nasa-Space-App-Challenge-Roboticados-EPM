
METRICS = [

    # ==========================================
    # 1. RADIATION
    # ==========================================

    {
        "id": 1,
        "name": "Active Radiation Dosimetry",
        "category": "radiation",
        "unit": "mSv",
        "description": "Measures real-time radiation exposure received by the astronaut.",
        "thresholds": None
    },
    {
        "id": 2,
        "name": "Passive Radiation Dosimetry",
        "category": "radiation",
        "unit": "mSv",
        "description": "Measures accumulated radiation exposure over a period of time.",
        "thresholds": None
    },

    # ==========================================
    # 2. MICROGRAVITY
    # ==========================================

    {
        "id": 3,
        "name": "Systolic Blood Pressure",
        "category": "microgravity",
        "unit": "mmHg",
        "description": "Measures arterial pressure when the heart contracts.",
        "thresholds": None
    },
    {
        "id": 4,
        "name": "Diastolic Blood Pressure",
        "category": "microgravity",
        "unit": "mmHg",
        "description": "Measures arterial pressure when the heart relaxes between beats.",
        "thresholds": None
    },
    {
        "id": 5,
        "name": "Continuous Blood Pressure",
        "category": "microgravity",
        "unit": "mmHg",
        "description": "Monitors blood pressure continuously over time.",
        "thresholds": None
    },
    {
        "id": 6,
        "name": "Heart Rate",
        "category": "microgravity",
        "unit": "BPM",
        "description": "Measures the number of heartbeats per minute.",
        "thresholds": None
    },
    {
        "id": 7,
        "name": "Standard ECG",
        "category": "microgravity",
        "unit": "mV",
        "description": "Records the electrical activity of the heart using a standard electrocardiogram.",
        "thresholds": None
    },
    {
        "id": 8,
        "name": "Holter ECG Monitoring",
        "category": "microgravity",
        "unit": "mV",
        "description": "Records the electrical activity of the heart over an extended period.",
        "thresholds": None
    },
    {
        "id": 9,
        "name": "Ocular Globe Ultrasound",
        "category": "microgravity",
        "unit": "mm",
        "description": "Evaluates the structure and dimensions of the eyeball using ultrasound.",
        "thresholds": None
    },
    {
        "id": 10,
        "name": "Optic Nerve Ultrasound",
        "category": "microgravity",
        "unit": "mm",
        "description": "Evaluates optic nerve sheath dimensions using ultrasound.",
        "thresholds": None
    },
    {
        "id": 11,
        "name": "Lumbar Spine Bone Densitometry (DEXA)",
        "category": "microgravity",
        "unit": "g/cm²",
        "description": "Measures bone mineral density in the lumbar spine.",
        "thresholds": None
    },
    {
        "id": 12,
        "name": "Hip Bone Densitometry (DEXA)",
        "category": "microgravity",
        "unit": "g/cm²",
        "description": "Measures bone mineral density in the hip.",
        "thresholds": None
    },
    {
        "id": 13,
        "name": "Whole-Body Bone Densitometry (DEXA)",
        "category": "microgravity",
        "unit": "g/cm²",
        "description": "Evaluates bone mineral density throughout the body.",
        "thresholds": None
    },
    {
        "id": 14,
        "name": "Blood Biochemical Analysis",
        "category": "microgravity",
        "unit": "Varies by analyte",
        "description": "Analyzes blood samples to evaluate biochemical and physiological markers.",
        "thresholds": None
    },
    {
        "id": 15,
        "name": "Urine Biochemical Analysis",
        "category": "microgravity",
        "unit": "Varies by analyte",
        "description": "Analyzes urine samples to evaluate biochemical and physiological markers.",
        "thresholds": None
    },
    {
        "id": 26,
        "name": "Blood Oxygen Saturation (SpO2)",
        "category": "microgravity",
        "unit": "%",
        "description": "Measures the percentage of hemoglobin saturated with oxygen.",
        "thresholds": None
    },
    {
        "id": 27,
        "name": "Heart Rate Variability (HRV)",
        "category": "microgravity",
        "unit": "ms",
        "description": "Measures variations in the time intervals between consecutive heartbeats.",
        "thresholds": None
    },
    {
        "id": 29,
        "name": "Bioelectrical Impedance Analysis (BIA)",
        "category": "microgravity",
        "unit": "Test-dependent",
        "description": "Estimates body composition using electrical impedance.",
        "thresholds": None
    },
    {
        "id": 30,
        "name": "Anthropometry and Body Mass Distribution",
        "category": "microgravity",
        "unit": "cm / kg",
        "description": "Measures body dimensions and mass distribution.",
        "thresholds": None
    },
    {
        "id": 31,
        "name": "Dynamic Vestibular Function Tests",
        "category": "microgravity",
        "unit": "Test-dependent",
        "description": "Evaluates vestibular function and balance responses during movement.",
        "thresholds": None
    },
    {
        "id": 32,
        "name": "Static Balance and Orthostatic Tests",
        "category": "microgravity",
        "unit": "Test-dependent",
        "description": "Evaluates postural stability and physiological responses to positional changes.",
        "thresholds": None
    },

    # ==========================================
    # 3. PSYCHOLOGY
    # ==========================================

    {
        "id": 22,
        "name": "Sleep Monitoring (Actigraphy)",
        "category": "psychology",
        "unit": "Hours",
        "description": "Tracks sleep patterns and duration using wearable actigraphy.",
        "thresholds": None
    },
    {
        "id": 23,
        "name": "Chronobiological Monitoring",
        "category": "psychology",
        "unit": "Hours",
        "description": "Monitors biological rest and alertness cycles.",
        "thresholds": None
    },
    {
        "id": 24,
        "name": "Neurocognitive Reaction Time",
        "category": "psychology",
        "unit": "ms",
        "description": "Evaluates cognitive response speed through reaction time tests.",
        "thresholds": None
    },
    {
        "id": 25,
        "name": "Mood and Psychological Well-being",
        "category": "psychology",
        "unit": "Score",
        "description": "Evaluates mood and psychological well-being through assessments.",
        "thresholds": None
    },

    # ==========================================
    # 4. ENVIRONMENT
    # ==========================================

    {
        "id": 16,
        "name": "Environmental Carbon Dioxide (CO2)",
        "category": "environment",
        "unit": "ppm",
        "description": "Monitors carbon dioxide concentration in the station environment.",
        "thresholds": None
    },
    {
        "id": 17,
        "name": "Environmental Oxygen (O2)",
        "category": "environment",
        "unit": "%",
        "description": "Monitors oxygen concentration in the station environment.",
        "thresholds": None
    },
    {
        "id": 18,
        "name": "Barometric Pressure",
        "category": "environment",
        "unit": "kPa",
        "description": "Measures atmospheric pressure inside the spacecraft.",
        "thresholds": None
    },
    {
        "id": 19,
        "name": "Surface Microbiological Monitoring",
        "category": "environment",
        "unit": "CFU / sample",
        "description": "Monitors microorganisms present on station surfaces.",
        "thresholds": None
    },
    {
        "id": 20,
        "name": "Air Microbiological Monitoring",
        "category": "environment",
        "unit": "CFU / m³",
        "description": "Monitors microbial contamination in the station atmosphere.",
        "thresholds": None
    },
    {
        "id": 21,
        "name": "Astronaut Microbiological Sampling",
        "category": "environment",
        "unit": "Test-dependent",
        "description": "Monitors microorganisms through biological samples collected from the astronaut.",
        "thresholds": None
    },
    {
        "id": 28,
        "name": "Core Body Temperature",
        "category": "environment",
        "unit": "°C",
        "description": "Measures the astronaut's internal body temperature.",
        "thresholds": None
    }
]

# Stable lookups used by the CSV importer and the data API. Keep METRICS as the
# single source of truth so a metric ID always maps to one category and unit.
METRICS_BY_ID = {metric["id"]: metric for metric in METRICS}
METRICS_BY_CATEGORY = {
    category: [metric for metric in METRICS if metric["category"] == category]
    for category in dict.fromkeys(metric["category"] for metric in METRICS)
}

if len(METRICS_BY_ID) != len(METRICS):
    raise ValueError("Metric IDs must be unique")

