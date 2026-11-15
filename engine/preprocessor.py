import re
import json
import os

class TextPreprocessor:
    def __init__(self, lexicon_path=None):
        if lexicon_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            lexicon_path = os.path.join(base_dir, "data", "oil_lexicon.json")
            
        self.lexicon = {}
        if os.path.exists(lexicon_path):
            with open(lexicon_path, "r", encoding="utf-8") as f:
                self.lexicon = json.load(f)
                
        self.acronyms = self.lexicon.get("acronyms", {})
        
        # Regex patterns for high energy indicators
        self.patterns = {
            "height": re.compile(r"(\d+(?:\.\d+)?)\s*(?:m|meter|meters|metre|metres|ft|feet)\b", re.IGNORECASE),
            "pressure": re.compile(r"(\d+(?:\.\d+)?)\s*(?:psi|bar|kpa|mpa)\b", re.IGNORECASE),
            "voltage": re.compile(r"(\d+(?:\.\d+)?)\s*(?:v|kv|volt|volts)\b", re.IGNORECASE),
            "weight": re.compile(r"(\d+(?:\.\d+)?)\s*(?:ton|tons|tonne|tonnes|kg|lbs)\b", re.IGNORECASE),
            "gas_conc": re.compile(r"(\d+(?:\.\d+)?)\s*(?:ppm|%?\s*lel)\b", re.IGNORECASE)
        }

    def expand_acronyms(self, text: str) -> str:
        """Expands oilfield abbreviations and acronyms while retaining the original term."""
        words = text.split()
        expanded_words = []
        for word in words:
            # Strip punctuation for lookup
            clean_word = re.sub(r"[^\w]", "", word).lower()
            if clean_word in self.acronyms:
                expansion = self.acronyms[clean_word]
                expanded_words.append(f"{word} ({expansion})")
            else:
                expanded_words.append(word)
        return " ".join(expanded_words)

    def extract_energy_metrics(self, text: str) -> dict:
        """Extracts physical measurements that indicate energy magnitude."""
        metrics = {
            "height_meters": None,
            "pressure_psi": None,
            "voltage_v": None,
            "weight_tons": None,
            "gas_concentration": None
        }
        
        # Height
        h_match = self.patterns["height"].search(text)
        if h_match:
            val = float(h_match.group(1))
            raw = h_match.group(0).lower()
            if "ft" in raw or "feet" in raw:
                val = val * 0.3048 # convert to meters
            metrics["height_meters"] = round(val, 2)
            
        # Pressure
        p_match = self.patterns["pressure"].search(text)
        if p_match:
            val = float(p_match.group(1))
            raw = p_match.group(0).lower()
            if "bar" in raw:
                val = val * 14.5038
            elif "kpa" in raw:
                val = val * 0.145038
            elif "mpa" in raw:
                val = val * 145.038
            metrics["pressure_psi"] = round(val, 1)
            
        # Voltage
        v_match = self.patterns["voltage"].search(text)
        if v_match:
            val = float(v_match.group(1))
            raw = v_match.group(0).lower()
            if "kv" in raw:
                val = val * 1000
            metrics["voltage_v"] = round(val, 1)
            
        # Weight
        w_match = self.patterns["weight"].search(text)
        if w_match:
            val = float(w_match.group(1))
            raw = w_match.group(0).lower()
            if "kg" in raw:
                val = val / 1000.0
            elif "lbs" in raw:
                val = val * 0.000453592
            metrics["weight_tons"] = round(val, 2)
            
        # Gas
        g_match = self.patterns["gas_conc"].search(text)
        if g_match:
            metrics["gas_concentration"] = g_match.group(0)
            
        return metrics

    def clean_text(self, text: str) -> str:
        """Basic normalization preserving barrier negation words like 'no', 'not', 'without'."""
        if not text:
            return ""
        # Normalize whitespace
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def preprocess_for_model(self, text: str) -> str:
        """Prepares text for TF-IDF vectorization with expanded domain context."""
        cleaned = self.clean_text(text)
        expanded = self.expand_acronyms(cleaned)
        return expanded
