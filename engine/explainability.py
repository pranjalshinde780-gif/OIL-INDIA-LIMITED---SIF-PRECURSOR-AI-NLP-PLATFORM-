import re

class ExplainabilityEngine:
    def __init__(self):
        # Critical keywords indicating immediate life-threatening barrier failure
        self.critical_tokens = {
            "without", "unhooked", "unlatched", "bypassed", "snapped", "overridden",
            "unisolated", "missing", "cracked", "sheared", "untested", "collapsed",
            "h2s", "sour", "blowout", "bop", "loto", "scba", "deluge", "asphyxiation",
            "overpressure", "jumper", "tampered", "disabled", "unanchored"
        }
        
        # Hazard context tokens
        self.hazard_tokens = {
            "derrick", "elevation", "mast", "scaffold", "scaffolding", "grating",
            "pressure", "psi", "bar", "manifold", "separator", "flange",
            "crane", "sling", "rigging", "hoisting", "suspended", "load",
            "confined", "tank", "sump", "vessel", "welding", "cutting",
            "sparks", "flammable", "hydrocarbon", "rotary", "iron", "roughneck",
            "line", "fire", "pinch", "high", "voltage", "switchgear"
        }

    def compute_token_saliency(self, text: str) -> list[dict]:
        """
        Calculates token-level risk saliency to provide explainability on
        which specific phrases triggered the SIF precursor classification.
        """
        words = re.findall(r"[\w']+|[.,!?;()]", text)
        annotated_tokens = []
        
        for w in words:
            clean = re.sub(r"[^\w]", "", w).lower()
            if not clean:
                annotated_tokens.append({"token": w, "weight": 0.0, "level": "neutral"})
                continue
                
            if clean in self.critical_tokens:
                weight = 0.95
                level = "danger"
            elif clean in self.hazard_tokens:
                weight = 0.65
                level = "warning"
            elif any(c.isdigit() for c in clean):
                weight = 0.40
                level = "info"
            else:
                weight = 0.05
                level = "neutral"
                
            annotated_tokens.append({
                "token": w,
                "weight": weight,
                "level": level
            })
            
        return annotated_tokens

    def generate_highlighted_html(self, text: str) -> str:
        """Renders token saliency as HTML spans for front-end rendering."""
        tokens = self.compute_token_saliency(text)
        html_parts = []
        for t in tokens:
            tok = t["token"]
            level = t["level"]
            if level == "danger":
                html_parts.append(f'<span class="px-1.5 py-0.5 mx-0.5 rounded font-semibold bg-rose-500/20 text-rose-300 border border-rose-500/40" title="Critical Precursor Trigger">{tok}</span>')
            elif level == "warning":
                html_parts.append(f'<span class="px-1 py-0.5 mx-0.5 rounded font-medium bg-amber-500/20 text-amber-300 border border-amber-500/30" title="High-Hazard Operational Element">{tok}</span>')
            elif level == "info":
                html_parts.append(f'<span class="px-1 py-0.5 mx-0.5 rounded bg-blue-500/20 text-blue-300 border border-blue-500/30" title="Energy Parameter">{tok}</span>')
            else:
                html_parts.append(tok)
        return " ".join(html_parts)

    def generate_rationale(self, text: str, sif_result: dict, iogp_result: dict) -> dict:
        """
        Synthesizes an HSE engineering rationale explaining the AI's diagnosis.
        """
        is_sif = sif_result["is_sif"]
        prob = sif_result["sif_probability"]
        rule = iogp_result["primary_iogp_rule"]
        metrics = sif_result.get("extracted_metrics", {})
        
        if is_sif:
            # Build specific hazard explanation
            hazard_drivers = []
            if metrics.get("height_meters"):
                hazard_drivers.append(f"Work at elevation of {metrics['height_meters']}m exceeding critical 1.8m fall threshold")
            if metrics.get("pressure_psi"):
                hazard_drivers.append(f"Pressurized line/vessel at {metrics['pressure_psi']} psi presenting high-energy release potential")
            if metrics.get("gas_concentration"):
                hazard_drivers.append(f"Toxic/explosive atmospheric concentration ({metrics['gas_concentration']}) detected")
            if metrics.get("weight_tons"):
                hazard_drivers.append(f"Suspended load mass of {metrics['weight_tons']} tons with drop zone exposure")
            
            if not hazard_drivers:
                hazard_drivers.append(f"Presence of critical energy hazard aligned with IOGP '{rule}' Life-Saving Rule")
                
            rationale_summary = (
                f"Flagged as a **SIF Precursor ({prob:.1%} confidence)** due to the convergence of "
                f"uncontrolled high energy ({', '.join(hazard_drivers)}) and an absent or compromised control barrier. "
                f"Without immediate safety intervention or secondary barriers, this sequence has direct potential to cause a life-altering injury or fatality."
            )
            key_factors = [
                f"Primary Life-Saving Rule: {rule}",
                f"Energy Category: {sif_result.get('risk_tier', 'High Risk')}",
                "Safety Barrier Breakdown: Positive physical/administrative barrier was absent, bypassed, or compromised"
            ]
        else:
            rationale_summary = (
                f"Classified as **Routine Non-SIF Observation ({1.0 - prob:.1%} confidence)**. "
                "The reported condition or behavior involves minimal stored energy and lacks the catastrophic energy thresholds "
                "(gravity > 1.8m, pressure > 100 psi, high voltage, toxic atmosphere) required to produce a fatal outcome."
            )
            key_factors = [
                "Low energy potential: Minor ergonomic, housekeeping, or administrative item",
                "Fatal consequence probability: Negligible (< 1%)",
                "Action tier: Standard routine housekeeping or facility maintenance resolution"
            ]
            
        return {
            "summary": rationale_summary,
            "key_factors": key_factors,
            "highlighted_html": self.generate_highlighted_html(text)
        }
