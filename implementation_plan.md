# SIH26165: AI/NLP Engine for SIF Precursor Detection in OIL Safety Reports

## Overview & Background
In Oil & Gas exploration and production (E&P), conventional safety pyramids assume that reducing minor incidents directly reduces fatalities. Modern safety science (Dekker, Conklin, Krause) has disproven this: **only 20–25% of minor incidents, unsafe conditions (UC), and unsafe acts (UA) contain SIF (Serious Injury and Fatality) precursors**. The remaining 75–80% are low-energy events with near-zero fatal potential.

For **Oil India Limited (OIL)**, thousands of unstructured safety reports are currently reviewed manually on monthly or quarterly cycles. High-risk signals—such as compromised blowout preventers (BOP), missing lockout-tagout (LOTO) on high-pressure lines, unharnessed work on derrick boards at 25m, or toxic $H_2S$ gas detector bypasses—remain buried in noisy text.

This project delivers an end-to-end, enterprise-grade AI/NLP system that:
1. **Identifies SIF Precursors** with high recall and confidence scoring using a hybrid physics/energy-aware NLP model.
2. **Tags incidents against IOGP Life-Saving Rules** (10 international standards adapted for OIL's operations).
3. **Conducts Automated Bowtie Analysis** (Threat $\rightarrow$ Preventative Barrier $\rightarrow$ Top Event $\rightarrow$ Mitigative Barrier $\rightarrow$ Consequence).
4. **Delivers Explainable AI (XAI)** with token-level risk highlighting and reasoning.
5. **Ranks Sites & Activities by SIF-Precursor Density** via an executive command dashboard for targeted safety interventions.
6. **Recommends CAPA (Corrective & Preventive Actions)** aligned with the industrial Hierarchy of Controls.

---

## User Review Required

> [!IMPORTANT]
> **Domain Lexicon & Safety Philosophy**:
> SIF detection requires a **high-recall safety-critical design**. A false positive requires a 30-second review by a safety engineer, but a false negative could cost a life. Our hybrid architecture combines:
> - TF-IDF n-gram NLP classification with probability calibration
> - Energy hazard and barrier degradation heuristics (OISD & IOGP Life-Saving Rules)
> - Acronym and dialect normalizer for OIL operational hubs (Assam-Arakan Basin: Duliajan, Digboi, Moran, Naharkatiya; Rajasthan Basin).

---

## Open Questions
1. **Data Source Integration**: Would you prefer the engine pre-loaded with a realistic synthetic dataset (1,200+ multi-site OIL field reports) with real-time CSV/Excel batch upload capability? *(Recommended: Yes, allows immediate evaluation and demonstration).*
2. **Preferred Web Interface**: We plan to implement a responsive, modern web dashboard (FastAPI backend + Tailwind CSS, ApexCharts, and Leaflet.js interactive maps) that runs standalone with `python run.py`. Does this meet your hackathon demo expectations?

---

## Proposed Changes

Grouped by architectural layer:

```
sih/
├── data/
│   ├── oil_safety_reports.csv          # 1,200+ realistic OIL incident dataset
│   └── oil_lexicon.json                # Oil & gas terminology, acronyms & energy rules
├── engine/
│   ├── __init__.py
│   ├── preprocessor.py                 # Text cleaning, acronym expansion & normalization
│   ├── sif_classifier.py               # Calibrated hybrid SIF precursor detection model
│   ├── iogp_tagger.py                  # 10 IOGP Life-Saving Rules multi-class classifier
│   ├── bowtie_analyzer.py              # Automated barrier & bowtie extraction engine
│   ├── explainability.py               # Token-level risk saliency & XAI rationale
│   └── capa_recommender.py             # Hierarchy of controls & corrective actions
├── app/
│   ├── __init__.py
│   ├── main.py                         # FastAPI web server and REST API endpoints
│   ├── static/
│   │   ├── css/style.css               # Dashboard styling & risk heatmaps
│   │   └── js/app.js                   # Client logic, ApexCharts, and Leaflet maps
│   └── templates/
│       ├── index.html                  # Main executive command center
│       ├── triage.html                 # Real-time incident triage & XAI inspector
│       └── batch.html                  # Batch upload & density ranking
├── tests/
│   ├── test_engine.py                  # Unit and integration test suite
│   └── test_api.py                     # API endpoint verification
├── run.py                              # One-click startup runner
└── requirements.txt                    # Project dependencies
```

---

### Data & Domain Layer

#### [NEW] [oil_lexicon.json](file:///c:/Users/Raju/Desktop/sih/data/oil_lexicon.json)
- Dictionary of Oil & Gas acronyms: `BOP`, `LOTO`, `PTW`, `SCBA`, `OCS`, `GGS`, `H2S`, `LEL`, `OIM`, `CPF`, `MP`, `Kelly`, `Derrick`, `Doghouse`, etc.
- Energy taxonomy (Gravity > 1.8m, Pressure > 100 psi, High Voltage > 440V, Toxic atmosphere, Mechanical kinetic, Flammable hydrocarbons).
- Barrier classification (Preventative vs. Mitigative; Physical, Engineered, Administrative, PPE).

#### [NEW] [dataset_generator.py](file:///c:/Users/Raju/Desktop/sih/data/dataset_generator.py)
- Generates 1,200+ realistic, high-fidelity safety observations across OIL operating divisions:
  - Drilling Rigs (Derrick, Rig floor, Mud tanks, Blowout preventers)
  - Production (Oil Collecting Stations, Gas Gathering Stations, Separators)
  - Crude Oil Pipelines (Naharkatiya-Barauni, pump stations, valve stations)
  - Workover & Well Services (Wireline, coiled tubing, cementing)
- Realistic label distribution: ~22% SIF precursors, ~78% non-SIF minor observations, mapped to 10 IOGP Life-Saving Rules.

---

### NLP & AI Engine Layer

#### [NEW] [preprocessor.py](file:///c:/Users/Raju/Desktop/sih/engine/preprocessor.py)
- Domain-specific text normalizer: resolves operational jargon, typos, and abbreviations.
- Energy magnitude extraction (e.g., extracts "25m", "3000 psi", "11kV", "H2S 50ppm").

#### [NEW] [sif_classifier.py](file:///c:/Users/Raju/Desktop/sih/engine/sif_classifier.py)
- Hybrid ML/NLP classification pipeline:
  - TF-IDF word & char n-grams (1, 3) + Calibrated Classifier ensemble.
  - Energy & Barrier Rule-Heuristic Layer that boosts recall for high-energy scenarios where barriers are compromised.
  - Generates `sif_score` (0.0 to 1.0), `sif_class` (SIF Precursor vs Non-SIF), and `risk_tier` (Low, Medium, High, Critical).

#### [NEW] [iogp_tagger.py](file:///c:/Users/Raju/Desktop/sih/engine/iogp_tagger.py)
- Classifies incident into the 10 IOGP Life-Saving Rules:
  1. Bypassing Safety Controls
  2. Confined Space
  3. Driving
  4. Energy Isolation
  5. Hot Work
  6. Line of Fire
  7. Safe Mechanical Lifting
  8. Toxic Gas / Hazardous Atmosphere
  9. Working at Height
  10. Work Authorization / Permit to Work

#### [NEW] [bowtie_analyzer.py](file:///c:/Users/Raju/Desktop/sih/engine/bowtie_analyzer.py)
- Automatically extracts the Bowtie elements from free text:
  - Hazard source & threat
  - Preventative barrier status (Failed / Missing / Intact)
  - Critical top event
  - Mitigative barrier status
  - Potential fatal consequence

#### [NEW] [explainability.py](file:///c:/Users/Raju/Desktop/sih/engine/explainability.py)
- Generates token-level risk saliency (colored highlights indicating high-risk words vs neutral words).
- Generates clear, plain-language engineering explanations: *Why did the AI flag this incident as a SIF precursor?*

#### [NEW] [capa_recommender.py](file:///c:/Users/Raju/Desktop/sih/engine/capa_recommender.py)
- Maps detected hazards to the Hierarchy of Controls (Elimination, Engineering, Administrative, PPE) tailored to OISD/OIL safety guidelines.

---

### Web Application & REST API Layer

#### [NEW] [main.py](file:///c:/Users/Raju/Desktop/sih/app/main.py)
- FastAPI application exposing REST endpoints:
  - `POST /api/analyze`: Single report deep analysis.
  - `POST /api/batch`: Bulk CSV/Excel processing.
  - `GET /api/stats`: Aggregate KPIs (precursor rate, top hazard categories, barrier degradation index).
  - `GET /api/site-density`: Ranked list of facilities by SIF Precursor density.
  - `GET /api/export`: Export enriched datasets.
  - `GET /api/briefing`: Generate printable SIF Incident Safety Briefing.

#### [NEW] [templates and static assets](file:///c:/Users/Raju/Desktop/sih/app/templates/index.html)
- Responsive, high-contrast industrial HSE dashboard:
  - **Triage Center**: Real-time text analysis with instant SIF gauge, token saliency visualization, dynamic Bowtie diagram, and CAPA checklist.
  - **Executive Analytics**: SIF precursor trends, IOGP category breakdown, barrier health tracking.
  - **Asset Risk Map**: Geo-spatial visualization of OIL facilities (Duliajan HQ, Digboi, Moran, Naharkatiya, Jaisalmer) with color-coded SIF precursor density.
  - **Batch Ingestion**: Drag-and-drop file uploader with live processing stats.

---

### Execution & Verification Layer

#### [NEW] [run.py](file:///c:/Users/Raju/Desktop/sih/run.py)
- CLI and web server launcher. Initialises data and trains/caches models automatically on first launch.

#### [NEW] [test_engine.py](file:///c:/Users/Raju/Desktop/sih/tests/test_engine.py)
- Automated unit test suite validating classification accuracy, recall on edge-case SIF reports, Bowtie generation, and API responses.

---

## Verification Plan

### Automated Tests
1. **Model Performance & Recall Verification**:
   - `python tests/test_engine.py`: Test SIF precursor detection recall ($\ge 92\%$), false-negative check on critical oilfield scenarios (high-pressure kicks, unharnessed derrick work, sour gas leaks).
   - Test IOGP multi-class classification and Bowtie extraction accuracy.
2. **API Endpoint Verification**:
   - Test `POST /api/analyze` with sample UA/UC/NM texts.
   - Test `POST /api/batch` with multi-row CSV upload.
   - Test `GET /api/site-density` ranking calculations.

### Manual Verification
1. Launch the web dashboard via `python run.py`.
2. Test interactive triage with diverse field reports:
   - *Working at Height*: "Roustabout spotted unhooked at 18m on monkey board."
   - *Energy Isolation*: "Technician started dismantling flange on separator line while 450 psi line was unisolated."
   - *Minor Non-SIF*: "Empty tea cup left on muster point bench."
3. Inspect the Token Saliency (XAI) and Bowtie diagram rendering.
4. Verify site SIF precursor density heatmap and CSV export.
