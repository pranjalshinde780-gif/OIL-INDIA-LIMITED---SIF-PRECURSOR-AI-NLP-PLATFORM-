#!/usr/bin/env python3
"""
Oil India Limited (OIL) - SIF Precursor Detection Engine
Startup Runner & Production Server 
"""
import os
import sys
import uvicorn

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data", "oil_safety_reports.csv")

def setup_environment():
    print("=" * 75)
    print("     OIL INDIA LIMITED - SIF PRECURSOR AI/NLP PLATFORM ")
    print("=" * 75)
    
    # Check dataset
    if not os.path.exists(DATA_FILE):
        print("[+] Generating authentic OIL field safety reports dataset...")
        from data.dataset_generator import generate_dataset
        generate_dataset()
    else:
        print("[✓] Found existing OIL safety dataset at data/oil_safety_reports.csv")
        
    # Check model
    from engine.sif_classifier import SIFClassifier
    classifier = SIFClassifier()
    if not classifier.is_trained:
        print("[+] Training calibrated hybrid NLP model on OIL safety data...")
        metrics = classifier.train()
        print(f"[✓] Model trained successfully: F1={metrics['f1_score']}, ROC-AUC={metrics['roc_auc']}")
    else:
        print("[✓] Pre-trained SIF Detection model loaded from cache.")
        
    print("\n" + "=" * 75)
    print("🚀 HSE Command Center & REST API Services Ready:")
    print("   • Executive Overview:   http://localhost:8000/")
    print("   • Live Triage Desk:     http://localhost:8000/triage")
    print("   • Batch Processing:     http://localhost:8000/batch")
    print("   • Interactive API Docs: http://localhost:8000/docs")
    print("=" * 75 + "\n")

def find_available_port(start_port=8000, max_attempts=20):
    import socket
    for port in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    return start_port

if __name__ == "__main__":
    setup_environment()
    default_port = int(os.environ.get("PORT", 8080))
    port = find_available_port(start_port=default_port)
    print(f"[*] Starting server on http://127.0.0.1:{port}")
    uvicorn.run("app.main:app", host="127.0.0.1", port=port, reload=False, log_level="info")
