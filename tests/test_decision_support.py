import unittest

from decision_support import DecisionSupportSystem


class DecisionSupportSystemTests(unittest.TestCase):
    def test_recommendation_for_healthy_scenario(self):
        system = DecisionSupportSystem()
        scenario = {
            "market_potential": "high",
            "expected_value": 0.9,
            "strategic_fit": "strong",
            "risk_level": "low",
            "cost": 0.2,
        }

        result = system.evaluate(scenario)

        self.assertEqual(result.prediction, "approve")
        self.assertGreaterEqual(result.confidence, 0.55)
        self.assertLessEqual(result.confidence, 0.99)
        self.assertTrue(result.rationale)
        self.assertTrue(result.factors)

    def test_recommendation_for_risky_scenario(self):
        system = DecisionSupportSystem()
        scenario = {
            "market_potential": "low",
            "expected_value": 0.1,
            "strategic_fit": "weak",
            "risk_level": "critical",
            "cost": 0.9,
        }

        result = system.evaluate(scenario)

        self.assertEqual(result.prediction, "reject")
        self.assertGreaterEqual(result.confidence, 0.55)
        self.assertTrue(result.factors)

    def test_invalid_scenario_raises_error(self):
        system = DecisionSupportSystem()

        with self.assertRaises(ValueError):
            system.evaluate({})

    def test_explain_output(self):
        system = DecisionSupportSystem()
        scenario = {
            "market_potential": "high",
            "expected_value": 0.8,
            "confidence": "high",
            "risk_level": "moderate",
        }

        explanation = system.explain(scenario)

        self.assertEqual(explanation["prediction"], "approve")
        self.assertIn("major_factors", explanation)
        self.assertIn("rationale", explanation)
        self.assertIn("model", explanation)


if __name__ == "__main__":
    unittest.main()
