import unittest
import os
import sys
from fastapi.testclient import TestClient

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app

class TestAPIEndpoints(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_get_dashboard_page(self):
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("OIL INDIA LIMITED", resp.text)
        self.assertIn("SIH26165", resp.text)

    def test_get_triage_page(self):
        resp = self.client.get("/triage")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Live Incident Triage", resp.text)

    def test_get_batch_page(self):
        resp = self.client.get("/batch")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Batch Incident Ingestion", resp.text)

    def test_api_analyze_sif_precursor(self):
        payload = {
            "text": "Floorman observed climbing the derrick ladder at 22m elevation without engaging fall arrest slider or safety harness lanyard.",
            "report_type": "Unsafe Act",
            "site_id": "OIL-RIG-01"
        }
        resp = self.client.post("/api/analyze", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "success")
        self.assertTrue(data["sif_evaluation"]["is_sif_precursor"])
        self.assertEqual(data["iogp_tagging"]["primary_iogp_rule"], "Working at Height")
        self.assertIn("bowtie_analysis", data)
        self.assertIn("explainable_ai", data)
        self.assertIn("capa_actions", data)

    def test_api_analyze_non_sif(self):
        payload = {
            "text": "Cardboard packaging boxes from spare parts delivery stacked unflattened behind store room.",
            "report_type": "Unsafe Condition",
            "site_id": "OIL-OCS-02"
        }
        resp = self.client.post("/api/analyze", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertFalse(data["sif_evaluation"]["is_sif_precursor"])
        self.assertLess(data["sif_evaluation"]["sif_probability"], 0.45)

    def test_api_dashboard_stats(self):
        resp = self.client.get("/api/dashboard-stats")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("kpis", data)
        self.assertGreater(data["kpis"]["total_reports"], 1000)
        self.assertIn("iogp_distribution", data)
        self.assertIn("site_rankings", data)

    def test_api_site_rankings(self):
        resp = self.client.get("/api/site-rankings")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(isinstance(data, list))
        self.assertGreater(len(data), 5)
        # Check first rank has sif_density_pct
        self.assertIn("sif_density_pct", data[0])

    def test_api_briefing_generation(self):
        payload = {
            "report_id": "OIL-TEST-001",
            "site_name": "Duliajan Rig #01",
            "incident_text": "Unharnessed worker spotted on monkey board at 20m",
            "iogp_rule": "Working at Height",
            "sif_probability": 0.95,
            "risk_tier": "Critical SIF Alert"
        }
        resp = self.client.post("/api/briefing", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("briefing_text", data)
        self.assertIn("OIL INDIA LIMITED", data["briefing_text"])

    def test_api_export_sif(self):
        resp = self.client.get("/api/export-sif")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.headers["content-type"], "text/csv; charset=utf-8")
        self.assertIn("OIL-HSE-", resp.text)

if __name__ == "__main__":
    unittest.main(verbosity=2)
