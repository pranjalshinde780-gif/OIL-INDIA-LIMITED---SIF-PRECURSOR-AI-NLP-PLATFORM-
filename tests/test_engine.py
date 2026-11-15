import unittest
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine import (
    TextPreprocessor,
    SIFClassifier,
    IOGPTagger,
    BowtieAnalyzer,
    ExplainabilityEngine,
    CAPARecommender
)

class TestSIFEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.preprocessor = TextPreprocessor()
        cls.classifier = SIFClassifier()
        if not cls.classifier.is_trained:
            cls.classifier.train()
        cls.iogp = IOGPTagger()
        cls.bowtie = BowtieAnalyzer()
        cls.xai = ExplainabilityEngine()
        cls.capa = CAPARecommender()

    def test_preprocessor_acronym_expansion(self):
        text = "Worker performed maintenance on BOP and manifold without LOTO"
        expanded = self.preprocessor.expand_acronyms(text)
        self.assertIn("blowout preventer", expanded.lower())
        self.assertIn("lockout tagout", expanded.lower())

    def test_energy_metrics_extraction(self):
        text = "Floorman at 22m elevation cracked 600 psi line with 25 ppm H2S"
        metrics = self.preprocessor.extract_energy_metrics(text)
        self.assertEqual(metrics["height_meters"], 22.0)
        self.assertEqual(metrics["pressure_psi"], 600.0)
        self.assertIn("25 ppm", metrics["gas_concentration"].lower())

    def test_sif_critical_working_at_height(self):
        text = "Roustabout climbing derrick ladder at 20m without safety harness or fall arrester"
        res = self.classifier.predict_one(text)
        self.assertEqual(res["is_sif"], 1)
        self.assertGreaterEqual(res["sif_probability"], 0.70)
        self.assertIn("Critical", res["risk_tier"])

    def test_sif_critical_pressure_loto(self):
        text = "Fitter opened discharge valve on crude line under 500 psi pressure without LOTO"
        res = self.classifier.predict_one(text)
        self.assertEqual(res["is_sif"], 1)
        self.assertGreaterEqual(res["sif_probability"], 0.70)

    def test_sif_critical_toxic_gas(self):
        text = "Worker entered well cellar pit where H2S alarm was beeping at 30 ppm without SCBA"
        res = self.classifier.predict_one(text)
        self.assertEqual(res["is_sif"], 1)
        self.assertGreaterEqual(res["sif_probability"], 0.70)

    def test_non_sif_routine_housekeeping(self):
        text = "Plastic water bottle found lying on floor in office corridor near water cooler"
        res = self.classifier.predict_one(text)
        self.assertEqual(res["is_sif"], 0)
        self.assertLess(res["sif_probability"], 0.45)
        self.assertEqual(res["risk_tier"], "Low Routine Risk")

    def test_iogp_rule_tagging(self):
        cases = [
            ("Monkey board operator working at 25m on rig mast", "Working at Height"),
            ("Cracking flange on 400 psi separator without LOTO", "Energy Isolation"),
            ("H2S toxic gas release detected in cellar pit", "Toxic Gas & Hazardous Atmosphere"),
            ("Mobile crane lifting 4 ton drill pipe with damaged wire rope", "Safe Mechanical Lifting"),
            ("Welding torch used near crude skimming pit emitting flammable gas", "Hot Work")
        ]
        for text, expected_rule in cases:
            tag = self.iogp.tag_incident(text, is_sif=True)
            self.assertEqual(tag["primary_iogp_rule"], expected_rule)

    def test_bowtie_generation(self):
        text = "Floorman unhooked harness at 20m elevation"
        bt = self.bowtie.generate_bowtie("Working at Height", text, is_sif=True)
        self.assertIn("Gravitational", bt["hazard"])
        self.assertIn("Fall", bt["top_event"])
        self.assertTrue(len(bt["preventative_barriers"]) > 0)
        self.assertTrue(len(bt["mitigative_barriers"]) > 0)

    def test_explainability_tokens_and_rationale(self):
        text = "Maintenance worker cracked high pressure line without LOTO"
        sif_res = self.classifier.predict_one(text)
        iogp_res = self.iogp.tag_incident(text, is_sif=True)
        xai_res = self.xai.generate_rationale(text, sif_res, iogp_res)
        
        self.assertIn("SIF Precursor", xai_res["summary"])
        self.assertTrue(len(xai_res["key_factors"]) >= 3)
        self.assertIn("span", xai_res["highlighted_html"])

    def test_capa_hierarchy_of_controls(self):
        capa = self.capa.recommend_actions("Energy Isolation", is_sif=True)
        levels = [item["level"] for item in capa["hierarchy"]]
        self.assertTrue(any("Elimination" in l for l in levels))
        self.assertTrue(any("Engineered" in l for l in levels))
        self.assertTrue(any("Administrative" in l for l in levels))
        self.assertTrue(any("PPE" in l for l in levels))
        self.assertIn("STOP WORK AUTHORITY", capa["priority"])

if __name__ == "__main__":
    unittest.main(verbosity=2)
