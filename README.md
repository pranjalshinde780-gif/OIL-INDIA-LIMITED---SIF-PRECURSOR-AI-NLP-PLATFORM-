# AI/NLP Engine to Detect Serious Injury & Fatality (SIF) Precursors in OIL Safety Reports

**Smart India Hackathon (SIH 2026)**  
**Problem Statement ID:** SIH26165  
**Organization:** Oil India Limited (OIL), Ministry of Petroleum and Natural Gas  
**Theme:** Smart Automation / Software  

---

## 📌 Executive Summary & Background

In the Oil & Gas exploration and production (E&P) industry, classical safety management adhered to Heinrich's Safety Triangle, assuming that reducing minor incidents directly reduced fatal accidents. Modern safety science (Dr. Matthew Hallowell, Krause, DEKRA, Campbell Institute) has disproven this: **only 20% to 25% of minor incidents, unsafe acts (UA), and unsafe conditions (UC) contain SIF (Serious Injury and Fatality) precursors**. The remaining 75–80% are low-energy occurrences with negligible fatal potential.

For **Oil India Limited (OIL)**, thousands of unstructured safety reports are currently triaged manually at periodic monthly/quarterly intervals. Critical signals—such as unlatched harnesses on monkey boards at 25m, unisolated lines under 600 psi pressure, toxic $H_2S$ gas detector bypasses, or damaged crane wire ropes—frequently remain buried under routine housekeeping observations.

This platform provides an end-to-end, real-time AI/NLP intelligence system that continuously screens safety reports to identify, prioritize, and alert HSE teams to SIF precursors before catastrophic loss occurs.

---

## 🚀 Key Capabilities & Features

1. **High-Recall Hybrid SIF Precursor Classifier**:
   - Integrates **calibrated TF-IDF n-gram NLP classification** with an **energy-barrier heuristic layer**.
   - Built on safety science principles: Flags incidents where high-energy sources (gravity > 1.8m, pressure > 100 psi, high voltage, toxic atmosphere) combine with absent, failed, or compromised barriers.
   - Prevents fatal false negatives with a high-recall, safety-critical architecture.

2. **IOGP Life-Saving Rules Categorization**:
   - Automatically categorizes observations into the 10 internationally recognized IOGP (International Association of Oil & Gas Producers) Life-Saving Rules tailored to OIL operations:
     - *Working at Height*, *Energy Isolation*, *Toxic Gas & Hazardous Atmosphere*, *Safe Mechanical Lifting*, *Confined Space*, *Hot Work*, *Line of Fire*, *Bypassing Safety Controls*, *Driving*, and *Permit to Work*.

3. **Automated Bowtie Risk Synthesis**:
   - Derives structured **Bowtie Risk Models** directly from incident narratives:
     - **Threat** $\rightarrow$ **Preventative Barriers** (Intact vs. Compromised status) $\rightarrow$ **Top Event** $\rightarrow$ **Mitigative Barriers** $\rightarrow$ **SIF Consequence**.

4. **Explainable AI (XAI) Token Saliency**:
   - Visualizes exact words and phrases that triggered the high-risk verdict using attention-weighted token highlighting (Red = Barrier Breakdown, Amber = Hazard Context, Blue = Energy Metric).
   - Generates natural-language engineering rationale explaining *why* the incident constitutes a fatal precursor.

5. **Hierarchy of Controls & CAPA Recommender**:
   - Generates actionable Corrective and Preventive Actions prioritized across:
     - 1. Elimination / Substitution
     - 2. Engineered Safeguards
     - 3. Administrative & PTW Protocols
     - 4. PPE & Life Support Equipment

6. **Facility SIF Precursor Density Ranking & Geo-Spatial Map**:
   - Ranks all Oil India Limited facilities, drilling rigs, and production stations by **SIF-precursor density** ($\frac{\text{SIF Precursors}}{\text{Total Reports}} \times 100$).
   - Interactive Leaflet.js map highlighting risk hotspots across the Assam-Arakan Basin (Duliajan HQ, Digboi, Moran, Naharkatiya) and Rajasthan Basin.

7. **Batch Ingestion & Printable Safety Briefing Generator**:
   - Drag-and-drop CSV / Excel processing engine for high-volume legacy logs.
   - One-click export of SIF alerts.
   - Generates printable Safety Stand-Down Briefings & Toolbox Talks for field supervisors.

---

## 🏗️ System Architecture

```
sih/
├── data/
│   ├── oil_lexicon.json            # Oilfield acronyms, energy thresholds & barrier taxonomies
│   ├── dataset_generator.py        # Realistic multi-site OIL field safety dataset generator
│   └── oil_safety_reports.csv      # 1,350+ realistic multi-facility reports dataset
├── engine/
│   ├── preprocessor.py             # Domain text cleaning, acronym expansion & physical extraction
│   ├── sif_classifier.py           # Calibrated hybrid ML model with energy-barrier booster
│   ├── iogp_tagger.py              # 10 IOGP Life-Saving Rules classifier
│   ├── bowtie_analyzer.py          # Automated Bowtie barrier risk extractor
│   ├── explainability.py           # Token-level XAI saliency & engineering rationale
│   └── capa_recommender.py         # Hierarchy of controls & corrective actions
├── app/
│   ├── main.py                     # FastAPI server & REST API endpoints
│   ├── static/
│   │   ├── css/style.css           # Industrial command center dark styling
│   │   └── js/app.js               # Client logic, ApexCharts & Leaflet map engine
│   └── templates/
│       ├── base.html               # Shared layout & navigation
│       ├── index.html              # Executive overview & site density rankings
│       ├── triage.html             # Live incident triage desk & XAI inspector
│       └── batch.html              # Bulk CSV/Excel batch upload & analysis
├── tests/
│   ├── test_engine.py              # Unit tests for NLP engine components
│   └── test_api.py                 # Integration tests for FastAPI endpoints
├── run.py                          # One-click startup runner
├── requirements.txt                # Python package dependencies
└── README.md                       # Documentation
```

---

## ⚡ Quick Start Guide

### 1. Requirements
Ensure Python 3.10+ is installed:
```bash
pip install -r requirements.txt
```

### 2. Launch the Platform
Run the single-click startup script:
```bash
python run.py
```

Open your browser to:
- **Executive Command Center:** [http://localhost:8080/](http://localhost:8080/)
- **Live Incident Triage & XAI:** [http://localhost:8080/triage](http://localhost:8080/triage)
- **Batch Report Ingestion:** [http://localhost:8080/batch](http://localhost:8080/batch)
- **Interactive OpenAPI Documentation:** [http://localhost:8080/docs](http://localhost:8080/docs)

---

## 🧪 Verification & Test Suite

Run the complete automated test suite (19 unit & API integration tests):
```bash
python -m unittest discover tests
```

---

## 📡 REST API Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/analyze` | Single incident analysis (SIF probability, IOGP tagging, Bowtie, XAI tokens, CAPA). |
| `POST` | `/api/batch-upload` | Upload CSV/Excel log of observations for bulk SIF screening. |
| `GET` | `/api/dashboard-stats` | Aggregated executive KPIs, IOGP breakdown, monthly trend, and facility rankings. |
| `GET` | `/api/site-rankings` | Facilities ranked by SIF Precursor Density (%). |
| `GET` | `/api/reports` | Filterable and paginated safety reports list. |
| `GET` | `/api/export-sif` | Download enriched CSV of all flagged SIF precursor events. |
| `POST` | `/api/briefing` | Generates a printable Safety Stand-Down briefing. |
