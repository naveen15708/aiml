# aiml

This repository contains an explainable AI decision-support system for small-business lending.

## Included

- `model.py`: a transparent weighted scorecard model that produces a recommendation, confidence, and factor-level explanation
- `server.py`: a lightweight HTTP server that serves the app and `/api/assess` endpoint
- `static/`: web UI assets for the decision-support experience
- `tests/test_model.py`: validation for recommendations, explanation quality, and invalid input handling

## Run locally

```bash
python3 server.py
```

Then open:

- http://localhost:8000
- API: http://localhost:8000/api/health

The app evaluates application inputs and returns a recommendation along with confidence and the strongest positive/negative factors driving the decision.
