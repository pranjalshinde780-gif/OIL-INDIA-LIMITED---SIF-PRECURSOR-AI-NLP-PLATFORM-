import os
import io
import json
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Optional, List

from fastapi import FastAPI, Request, File, UploadFile, Query, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from engine import (
    TextPreprocessor,
    SIFClassifier,
    IOGPTagger,
    BowtieAnalyzer,
    ExplainabilityEngine,
    CAPARecommender
)

# Initialize FastAPI App
app = FastAPI(
    title="OIL SIF Precursor Detection Engine",
    description="AI/NLP Intelligence Platform for Oil India Limited ",
    version="1.0.0"
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
REPORTS_CSV = os.path.join(DATA_DIR, "oil_safety_reports.csv")
LEXICON_PATH = os.path.join(DATA_DIR, "oil_lexicon.json")

# Mount Static Files and Templates
static_dir = os.path.join(os.path.dirname(__file__), "static")
templates_dir = os.path.join(os.path.dirname(__file__), "templates")
os.makedirs(static_dir, exist_ok=True)
os.makedirs(os.path.join(static_dir, "css"), exist_ok=True)
os.makedirs(os.path.join(static_dir, "js"), exist_ok=True)
os.makedirs(templates_dir, exist_ok=True)

app.mount("/static", StaticFiles(directory=static_dir), name="static")
templates = Jinja2Templates(directory=templates_dir)

# Initialize AI/NLP Engines
print("Initializing AI/NLP Engine components...")
classifier = SIFClassifier()
iogp_tagger = IOGPTagger(LEXICON_PATH)
bowtie_analyzer = BowtieAnalyzer()
explainability = ExplainabilityEngine()
capa_recommender = CAPARecommender()
preprocessor = TextPreprocessor(LEXICON_PATH)

# Ensure model is trained
if not classifier.is_trained:
    print("Training SIF Classifier model on baseline OIL safety data...")
    classifier.train(REPORTS_CSV)

# In-memory dataframe cache for fast dashboard analytics
def load_dataset() -> pd.DataFrame:
    if os.path.exists(REPORTS_CSV):
        return pd.read_csv(REPORTS_CSV)
    return pd.DataFrame()

df_reports = load_dataset()

# -------------------------------------------------------------
# Pydantic Schemas
# -------------------------------------------------------------
class IncidentAnalysisRequest(BaseModel):
    text: str
    report_type: Optional[str] = "Unsafe Act"
    site_id: Optional[str] = "OIL-RIG-01"
    reporter_role: Optional[str] = "Safety Officer"

class BriefingRequest(BaseModel):
    report_id: Optional[str] = "NEW-REPORT"
    site_name: str
    incident_text: str
    iogp_rule: str
    sif_probability: float
    risk_tier: str

# -------------------------------------------------------------
# Frontend Routes
# -------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def home_dashboard(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={"page": "dashboard"})

@app.get("/triage", response_class=HTMLResponse)
async def live_triage_desk(request: Request):
    return templates.TemplateResponse(request=request, name="triage.html", context={"page": "triage"})

@app.get("/batch", response_class=HTMLResponse)
async def batch_upload_view(request: Request):
    return templates.TemplateResponse(request=request, name="batch.html", context={"page": "batch"})

# -------------------------------------------------------------
# REST API Endpoints
# -------------------------------------------------------------
@app.post("/api/analyze")
async def analyze_incident(req: IncidentAnalysisRequest):
    """
    Core AI/NLP deep-dive endpoint for single report triage.
    Executes SIF classification, IOGP tagging, Bowtie extraction,
    XAI token saliency, and CAPA generation.
    """
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Incident text cannot be empty.")

    # 1. SIF Precursor Classification & Energy-Barrier Heuristics
    sif_res = classifier.predict_one(req.text)
    is_sif = bool(sif_res["is_sif"])

    # 2. IOGP Life-Saving Rules Tagging
    iogp_res = iogp_tagger.tag_incident(req.text, is_sif=is_sif)

    # 3. Bowtie Risk Model Analysis
    bowtie_res = bowtie_analyzer.generate_bowtie(iogp_res["primary_iogp_rule"], req.text, is_sif=is_sif)

    # 4. Explainable AI (XAI) Token Saliency & Rationale
    xai_res = explainability.generate_rationale(req.text, sif_res, iogp_res)

    # 5. CAPA Action Recommendations (Hierarchy of Controls)
    capa_res = capa_recommender.recommend_actions(iogp_res["primary_iogp_rule"], is_sif=is_sif)

    # 6. Physical energy extraction metrics
    metrics = sif_res.get("extracted_metrics", {})

    return {
        "status": "success",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "sif_evaluation": {
            "is_sif_precursor": is_sif,
            "category": "SIF Precursor" if is_sif else "Routine Non-SIF",
            "sif_probability": sif_res["sif_probability"],
            "ml_probability": sif_res["ml_probability"],
            "confidence": sif_res["confidence"],
            "risk_tier": sif_res["risk_tier"],
            "rule_boosted": sif_res["rule_boosted"],
            "rule_reason": sif_res["rule_reason"]
        },
        "iogp_tagging": iogp_res,
        "energy_metrics": metrics,
        "bowtie_analysis": bowtie_res,
        "explainable_ai": xai_res,
        "capa_actions": capa_res
    }

@app.get("/api/dashboard-stats")
async def get_dashboard_stats():
    """
    Aggregated HSE analytics across all triaged reports in the system.
    """
    global df_reports
    if df_reports.empty:
        df_reports = load_dataset()

    total_reports = len(df_reports)
    sif_count = int(df_reports["is_sif_precursor"].sum()) if "is_sif_precursor" in df_reports else 0
    non_sif_count = total_reports - sif_count
    sif_density = round((sif_count / total_reports * 100), 1) if total_reports > 0 else 0.0

    # IOGP Breakdown (filter to SIF precursors for critical rule distribution)
    sif_df = df_reports[df_reports["is_sif_precursor"] == 1]
    iogp_counts = sif_df["iogp_rule"].value_counts().to_dict()

    # Barrier status
    barrier_counts = sif_df["barrier_status"].value_counts().to_dict() if "barrier_status" in sif_df else {}

    # Severity distribution
    severity_counts = df_reports["potential_severity"].value_counts().to_dict() if "potential_severity" in df_reports else {}

    # Facility density ranking
    site_group = df_reports.groupby("site_name").agg(
        total_reports=("report_id", "count"),
        sif_precursors=("is_sif_precursor", "sum"),
        latitude=("latitude", "first"),
        longitude=("longitude", "first"),
        facility_type=("facility_type", "first"),
        basin=("basin", "first")
    ).reset_index()

    site_group["sif_density_pct"] = (site_group["sif_precursors"] / site_group["total_reports"] * 100).round(1)
    site_group = site_group.sort_values(by="sif_density_pct", ascending=False)
    site_rankings = site_group.to_dict(orient="records")

    # Time series approximation (by month)
    monthly_trend = {
        "categories": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep"],
        "total_reports": [140, 155, 162, 138, 149, 158, 142, 150, 156],
        "sif_precursors": [32, 38, 41, 30, 36, 40, 31, 34, 35]
    }

    return {
        "kpis": {
            "total_reports": total_reports,
            "sif_precursors": sif_count,
            "non_sif_reports": non_sif_count,
            "sif_precursor_rate_pct": sif_density,
            "high_risk_facilities_count": len([s for s in site_rankings if s["sif_density_pct"] >= 25.0])
        },
        "iogp_distribution": iogp_counts,
        "barrier_distribution": barrier_counts,
        "severity_distribution": severity_counts,
        "site_rankings": site_rankings,
        "monthly_trend": monthly_trend
    }

@app.get("/api/site-rankings")
async def get_site_rankings():
    """
    Ranks Oil India Limited facilities by SIF Precursor density to focus
    preventive safety audits where fatal risk is concentrated.
    """
    global df_reports
    if df_reports.empty:
        df_reports = load_dataset()

    site_group = df_reports.groupby(["site_id", "site_name", "facility_type", "basin"]).agg(
        total_reports=("report_id", "count"),
        sif_precursors=("is_sif_precursor", "sum"),
        latitude=("latitude", "first"),
        longitude=("longitude", "first")
    ).reset_index()

    site_group["sif_density_pct"] = (site_group["sif_precursors"] / site_group["total_reports"] * 100).round(1)
    site_group["risk_level"] = site_group["sif_density_pct"].apply(
        lambda x: "CRITICAL" if x >= 30.0 else ("HIGH" if x >= 24.0 else ("MODERATE" if x >= 15.0 else "LOW"))
    )
    site_group = site_group.sort_values(by="sif_density_pct", ascending=False)
    return site_group.to_dict(orient="records")

@app.get("/api/reports")
async def list_reports(
    sif_only: Optional[bool] = False,
    site_id: Optional[str] = None,
    iogp_rule: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """
    Retrieves filtered list of safety reports from database.
    """
    global df_reports
    if df_reports.empty:
        df_reports = load_dataset()

    filtered = df_reports.copy()
    if sif_only:
        filtered = filtered[filtered["is_sif_precursor"] == 1]
    if site_id:
        filtered = filtered[filtered["site_id"] == site_id]
    if iogp_rule and iogp_rule != "All":
        filtered = filtered[filtered["iogp_rule"] == iogp_rule]

    total_count = len(filtered)
    page_items = filtered.iloc[offset : offset + limit].to_dict(orient="records")

    return {
        "total": total_count,
        "limit": limit,
        "offset": offset,
        "reports": page_items
    }

@app.post("/api/batch-upload")
async def batch_upload_reports(file: UploadFile = File(...)):
    """
    Processes batch CSV or Excel files containing field observations.
    Runs automated SIF classification and IOGP tagging on each entry.
    """
    contents = await file.read()
    filename = file.filename.lower()

    try:
        if filename.endswith(".csv"):
            df_in = pd.read_csv(io.BytesIO(contents))
        elif filename.endswith((".xlsx", ".xls")):
            df_in = pd.read_excel(io.BytesIO(contents))
        else:
            raise HTTPException(status_code=400, detail="Invalid file format. Please upload a CSV or Excel file.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse file: {str(e)}")

    # Detect text column
    text_cols = [c for c in df_in.columns if any(k in c.lower() for k in ["desc", "detail", "text", "narrative", "observation", "report"])]
    if not text_cols:
        text_col = df_in.columns[0]
    else:
        text_col = text_cols[0]

    results = []
    sif_count = 0

    for idx, row in df_in.iterrows():
        text = str(row[text_col])
        if not text.strip() or text.lower() == "nan":
            continue

        sif_res = classifier.predict_one(text)
        is_sif = bool(sif_res["is_sif"])
        if is_sif:
            sif_count += 1

        iogp_res = iogp_tagger.tag_incident(text, is_sif=is_sif)

        res_item = {
            "row_index": idx + 1,
            "text": text,
            "is_sif_precursor": is_sif,
            "sif_probability": sif_res["sif_probability"],
            "risk_tier": sif_res["risk_tier"],
            "iogp_rule": iogp_res["primary_iogp_rule"],
            "rule_boosted": sif_res["rule_boosted"],
            "rule_reason": sif_res["rule_reason"]
        }
        results.append(res_item)

    total_processed = len(results)
    sif_density = round((sif_count / total_processed * 100), 1) if total_processed > 0 else 0.0

    return {
        "status": "success",
        "filename": file.filename,
        "total_records": total_processed,
        "sif_precursors_detected": sif_count,
        "sif_density_pct": sif_density,
        "sample_results": results[:50],
        "all_results": results
    }

@app.get("/api/export-sif")
async def export_sif_reports():
    """
    Exports all flagged SIF precursor observations as a CSV for HSE leadership.
    """
    global df_reports
    if df_reports.empty:
        df_reports = load_dataset()

    sif_df = df_reports[df_reports["is_sif_precursor"] == 1]
    output = io.StringIO()
    sif_df.to_csv(output, index=False)
    output.seek(0)

    filename = f"OIL_SIF_Precursors_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode()),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@app.post("/api/briefing")
async def generate_briefing(b: BriefingRequest):
    """
    Generates a printable, executive HSE Safety Stand-Down & Toolbox Talk briefing.
    """
    briefing_content = f"""
========================================================================================
                      OIL INDIA LIMITED - HSE SAFETY ALERT & BRIEFING
                              SERIOUS INJURY & FATALITY (SIF) PRECURSOR
========================================================================================
Date: {datetime.now().strftime('%d-%b-%Y')}                  Facility: {b.site_name}
Reference: {b.report_id}                  Risk Tier: {b.risk_tier.upper()}
SIF Probability: {b.sif_probability:.1%}                     IOGP Rule: {b.iogp_rule}
----------------------------------------------------------------------------------------

1. INCIDENT DESCRIPTION:
   "{b.incident_text}"

2. WHY THIS IS A SIF PRECURSOR:
   The presence of high energy combined with absent or compromised control barriers
   indicates that without immediate intervention, this event possessed direct potential
   to result in a serious, irreversible, or fatal injury.

3. MANDATORY LIFE-SAVING ACTIONS:
   - Immediately invoke Stop Work Authority (SWA) if similar conditions are observed.
   - Verify 100% adherence to IOGP Life-Saving Rule: [{b.iogp_rule}].
   - Conduct pre-job Job Safety Analysis (JSA) and verify valid Permit to Work (PTW).
   - Ensure all physical barriers (LOTO, Fall Arrest, Gas Monitoring) are active.

4. DISCUSSION POINTS FOR CREW TOOLBOX TALK:
   Q1: Have we identified similar hazards during today's shift operations?
   Q2: Are all critical barriers in place and verified before starting work?
   Q3: Who has the authority to stop work if conditions become unsafe? (Answer: EVERYONE).

Authorized by: Chief General Manager (HSE), Oil India Limited
========================================================================================
    """.strip()

    return {"briefing_text": briefing_content}
