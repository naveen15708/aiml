# aiml

This repository contains a lightweight explainable AI decision-support system.

## What is included

- `decision_support/engine.py`: a weighted scoring model that predicts an `approve` or `reject` recommendation
- `decision_support/__init__.py`: package exports
- `tests/test_decision_support.py`: focused validation for prediction, confidence, and explanations

## Example usage

```python
from decision_support import DecisionSupportSystem

system = DecisionSupportSystem()
scenario = {
    "market_potential": "high",
    "expected_value": 0.9,
    "strategic_fit": "strong",
    "risk_level": "low",
    "cost": 0.2,
}

print(system.recommend(scenario))
```

The system returns a prediction, confidence score, major contributing factors, and human-readable rationale for the recommendation.
