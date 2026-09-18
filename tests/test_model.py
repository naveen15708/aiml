import unittest

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


if __name__ == "__main__":
    unittest.main()
