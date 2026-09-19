import unittest

from components.reporting import build_report_pdf
from model import assess


GOOD = {
    "credit_score": 760,
    "debt_to_income": 25,
    "annual_income": 180000,
    "cash_reserves": 80000,
    "business_years": 7,
    "requested_amount": 40000,
}


class AssessmentTests(unittest.TestCase):
    def test_returns_recommendation_and_all_explanations(self):
        result = assess(GOOD)
        self.assertEqual(result["recommendation"], "Likely eligible")
        self.assertEqual(len(result["factors"]), 6)
        self.assertTrue(0 < result["confidence"] <= 1)

    def test_high_debt_weakens_result(self):
        result = assess({**GOOD, "debt_to_income": 90})
        debt = next(f for f in result["factors"] if f["key"] == "debt_to_income")
        self.assertEqual(debt["direction"], "weakens")

    def test_invalid_input_is_rejected(self):
        with self.assertRaises(ValueError):
            assess({**GOOD, "credit_score": 200})

    def test_pdf_report_is_generated_for_current_scenario(self):
        payload = build_report_pdf(
            domain="Business lending",
            values={
                "credit_score": 735,
                "debt_to_income": 32,
                "annual_income": 145000,
                "cash_reserves": 65000,
                "business_years": 8,
                "requested_amount": 75000,
            },
            result={
                "probability": 0.42,
                "level": "Medium",
                "confidence": 0.7,
                "plain_language": "The model estimates 42% medium risk.",
                "factors": [
                    {"label": "Credit score", "impact": 0.18},
                    {"label": "Debt-to-income", "impact": -0.12},
                ],
            },
            lime_values=[{"feature": "credit_score", "impact": 0.2}, {"feature": "debt_to_income", "impact": -0.1}],
        )
        self.assertTrue(payload.startswith(b"%PDF"))
        self.assertGreater(len(payload), 200)


if __name__ == "__main__":
    unittest.main()
