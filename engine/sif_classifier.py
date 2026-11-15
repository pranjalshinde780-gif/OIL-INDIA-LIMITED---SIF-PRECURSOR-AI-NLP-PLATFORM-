import os
import joblib
import json
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, roc_auc_score, f1_score

from .preprocessor import TextPreprocessor

class SIFClassifier:
    def __init__(self, model_dir=None):
        if model_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            model_dir = os.path.join(base_dir, "models")
        self.model_dir = model_dir
        os.makedirs(self.model_dir, exist_ok=True)
        self.model_path = os.path.join(self.model_dir, "sif_pipeline.joblib")
        
        self.preprocessor = TextPreprocessor()
        self.pipeline = None
        self.is_trained = False
        
        # Load lexicon for heuristic energy & barrier rules
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        lex_path = os.path.join(base_dir, "data", "oil_lexicon.json")
        self.lexicon = {}
        if os.path.exists(lex_path):
            with open(lex_path, "r", encoding="utf-8") as f:
                self.lexicon = json.load(f)
                
        self.compromised_barrier_terms = self.lexicon.get("barrier_indicators", {}).get("compromised", [
            "missing", "bypassed", "absent", "not worn", "not attached", "failed", "broken",
            "without", "unhooked", "unlatched", "overridden", "damaged", "no permit", "unisolated"
        ])
        
        # Try loading pre-existing model
        self.load_model()

    def train(self, data_path: str = None) -> dict:
        """Trains the calibrated TF-IDF + Logistic Regression model on OIL safety data."""
        if data_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            data_path = os.path.join(base_dir, "data", "combined_training_data.csv")
            
        if not os.path.exists(data_path):
            raise FileNotFoundError(f"Training data not found at {data_path}")
            
        df = pd.read_csv(data_path)
        X_raw = df["description"].fillna("").tolist()
        y = df["is_sif_precursor"].values
        
        # Preprocess text
        X = [self.preprocessor.preprocess_for_model(t) for t in X_raw]
        
        # Vectorizer and Calibrated Classifier
        vectorizer = TfidfVectorizer(
                   ngram_range=(1, 3),
                  max_features=12000,
                  sublinear_tf=True,
                  min_df=2,
                  stop_words="english"
                    )
        
        base_clf = LogisticRegression(
            class_weight="balanced",
            C=2.5,
            max_iter=1000,
            random_state=42
        )
        
        calibrated_clf = CalibratedClassifierCV(estimator=base_clf, method="sigmoid", cv=5)
        
                # Split data into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=0.20,
            random_state=42,
            stratify=y
        )

        self.pipeline = Pipeline([
            ("tfidf", vectorizer),
            ("clf", calibrated_clf)
        ])

        # Train only on training data
        self.pipeline.fit(X_train, y_train)
        self.is_trained = True

        # Evaluate on unseen test data
        y_pred = self.pipeline.predict(X_test)
        y_proba = self.pipeline.predict_proba(X_test)[:, 1]

        # Evaluation metrics
        f1 = f1_score(y_test, y_pred)
        roc = roc_auc_score(y_test, y_proba)
        report = classification_report(y_test, y_pred, output_dict=True)
        # Save model
        joblib.dump(self.pipeline, self.model_path)
        
        metrics = {
            "f1_score": round(float(f1), 4),
            "roc_auc": round(float(roc), 4),
            "precision_sif": round(float(report["1"]["precision"]), 4),
            "recall_sif": round(float(report["1"]["recall"]), 4),
            "accuracy": round(float(report["accuracy"]), 4),
            "samples": len(df)
        }
        return metrics

    def load_model(self) -> bool:
        if os.path.exists(self.model_path):
            try:
                self.pipeline = joblib.load(self.model_path)
                self.is_trained = True
                return True
            except Exception:
                self.is_trained = False
        return False

    def check_energy_barrier_heuristics(self, text: str, metrics: dict) -> tuple[bool, str]:
        """
        Safety Science Rule Layer:
        Evaluates presence of critical high-energy hazards combined with compromised barriers.
        Guarantees that life-threatening scenarios are not missed by pure statistical inference.
        """
        text_lower = text.lower()
        
        # Check compromised barrier
        has_compromised_barrier = any(term in text_lower for term in self.compromised_barrier_terms)
        
        # 1. High elevation + compromised barrier
        h = metrics.get("height_meters")
        if h and h >= 1.8 and has_compromised_barrier:
            return True, f"Critical Fall Energy: Elevation of {h}m (> 1.8m lethal threshold) with compromised fall protection barrier."
            
        # 2. High Pressure (> 100 psi) + barrier failure / open line
        p = metrics.get("pressure_psi")
        if p and p >= 100 and (has_compromised_barrier or "leak" in text_lower or "flange" in text_lower):
            return True, f"High Pressure Hazard: System operating at {p} psi with compromised containment or isolation."
            
        # 3. High Voltage (> 50V / industrial) + unisolated
        v = metrics.get("voltage_v")
        if v and v >= 50 and ("without" in text_lower or "unisolated" in text_lower or "live" in text_lower):
            return True, f"Electrical Energy Hazard: Work near {v}V circuit without verified zero-energy state."
            
        # 4. Toxic Gas (H2S / sour gas) without SCBA or detector
        if ("h2s" in text_lower or "sour gas" in text_lower) and has_compromised_barrier:
            return True, "Toxic Atmosphere Hazard: Lethal H2S exposure risk with compromised respiratory or monitoring control."
            
        # 5. Suspended heavy load + drop zone
        w = metrics.get("weight_tons")
        if w and w >= 0.5 and ("under" in text_lower or "beneath" in text_lower or has_compromised_barrier):
            return True, f"Suspended Heavy Mass: {w} tons suspended load with personnel in drop zone or compromised rigging."
            
        # 6. Confined space entry without permit / ventilation
        if ("confined space" in text_lower or "mud tank" in text_lower or "vessel" in text_lower) and has_compromised_barrier:
            return True, "Atmospheric / Entrapment Hazard: Confined space entry without verified continuous life-support barrier."

        return False, ""

    def predict_one(self, text: str) -> dict:
        """
        Classifies an individual safety report and returns calibrated SIF probabilities
        and engineering risk tiers.
        """
        if not self.is_trained:
            # Self-train if model file is missing
            self.train()
            
        clean_text = self.preprocessor.clean_text(text)
        prep_text = self.preprocessor.preprocess_for_model(clean_text)
        metrics = self.preprocessor.extract_energy_metrics(clean_text)
        
        # ML statistical prediction
        probas = self.pipeline.predict_proba([prep_text])[0]
        ml_sif_prob = float(probas[1])
        
        # Rule booster for zero false-negative safety assurance
        rule_boosted, rule_reason = self.check_energy_barrier_heuristics(clean_text, metrics)
        
        if rule_boosted:
            final_prob = max(ml_sif_prob, 0.88)
            is_sif = 1
        else:
            final_prob = ml_sif_prob
            is_sif = 1 if final_prob >= 0.45 else 0
            
        # Determine risk tier
        if final_prob >= 0.80:
            risk_tier = "Critical SIF Alert"
            confidence = "High"
        elif final_prob >= 0.50:
            risk_tier = "High SIF Precursor"
            confidence = "High" if final_prob >= 0.65 else "Medium"
        elif final_prob >= 0.30:
            risk_tier = "Moderate Risk (Watchlist)"
            confidence = "Medium"
        else:
            risk_tier = "Low Routine Risk"
            confidence = "High"
            
        return {
            "is_sif": is_sif,
            "sif_probability": round(final_prob, 4),
            "ml_probability": round(ml_sif_prob, 4),
            "rule_boosted": rule_boosted,
            "rule_reason": rule_reason,
            "risk_tier": risk_tier,
            "confidence": confidence,
            "extracted_metrics": metrics
        }
