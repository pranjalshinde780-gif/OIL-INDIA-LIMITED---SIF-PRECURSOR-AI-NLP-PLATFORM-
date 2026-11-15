import os
import json
import re
from .preprocessor import TextPreprocessor

class IOGPTagger:
    def __init__(self, lexicon_path=None):
        if lexicon_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            lexicon_path = os.path.join(base_dir, "data", "oil_lexicon.json")
            
        self.rules = {}
        if os.path.exists(lexicon_path):
            with open(lexicon_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.rules = data.get("iogp_rules", {})
                
        self.preprocessor = TextPreprocessor()

    def tag_incident(self, text: str, is_sif: bool = True) -> dict:
        """
        Tags an incident description against the 10 IOGP Life-Saving Rules.
        Returns the top matching rule, confidence, matched keywords, and description.
        """
        text_lower = text.lower()
        expanded_text = self.preprocessor.expand_acronyms(text).lower()
        combined_text = f"{text_lower} {expanded_text}"
        
        scores = {}
        matched_details = {}
        
        for rule_name, rule_data in self.rules.items():
            keywords = rule_data.get("keywords", [])
            match_count = 0
            found_keywords = []
            
            for kw in keywords:
                # Check keyword presence
                pattern = r"\b" + re.escape(kw) + r"\b"
                matches = re.findall(pattern, combined_text)
                if matches:
                    match_count += len(matches)
                    found_keywords.append(kw)
                    
            if match_count > 0:
                scores[rule_name] = match_count
                matched_details[rule_name] = found_keywords
                
        if scores:
            best_rule = max(scores, key=scores.get)
            match_keywords = matched_details[best_rule]
            confidence = min(0.95, 0.60 + (scores[best_rule] * 0.12))
            description = self.rules[best_rule].get("description", "")
        else:
            if is_sif:
                # Fallback based on general oilfield hazard
                best_rule = "Work Authorization & Permit to Work"
                match_keywords = ["general hazard"]
                confidence = 0.50
                description = "Work with a valid permit when required; understand scope and critical controls."
            else:
                best_rule = "Non-Critical / General HSE"
                match_keywords = ["routine"]
                confidence = 0.90
                description = "Routine facility housekeeping or minor administrative observation."
                
        return {
            "primary_iogp_rule": best_rule,
            "rule_description": description,
            "matched_keywords": list(set(match_keywords)),
            "tag_confidence": round(confidence, 2)
        }
