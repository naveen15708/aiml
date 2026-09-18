from __future__ import annotations

from typing import Any, Dict

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from decision_support import DecisionSupportSystem

app = FastAPI(title="Explainable Decision Support")
engine = DecisionSupportSystem()


class ScenarioInput(BaseModel):
    scenario: Dict[str, Any]


HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Explainable Decision Support</title>
    <style>
      body {
        font-family: Arial, sans-serif;
        max-width: 900px;
        margin: 40px auto;
        padding: 24px;
        background: #f4f7fb;
        color: #1f2937;
      }
      .card {
        background: white;
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.08);
      }
      textarea, button {
        width: 100%;
        margin-top: 12px;
        font: inherit;
      }
      textarea {
        min-height: 200px;
        padding: 12px;
        border-radius: 8px;
        border: 1px solid #d1d5db;
      }
      button {
        background: #2563eb;
        color: white;
        border: none;
        padding: 12px 16px;
        border-radius: 8px;
        cursor: pointer;
      }
      pre {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 16px;
        overflow: auto;
      }
    </style>
  </head>
  <body>
    <div class="card">
      <h1>Explainable Decision Support System</h1>
      <p>Paste a scenario as JSON and the model will return a recommendation, confidence, and major influencing factors.</p>
      <textarea id="scenarioInput">{
  "market_potential": "high",
  "expected_value": 0.9,
  "strategic_fit": "strong",
  "risk_level": "low",
  "cost": 0.2
}</textarea>
      <button onclick="submitScenario()">Evaluate</button>
      <h2>Result</h2>
      <pre id="result">Waiting for analysis...</pre>
    </div>

    <script>
      async function submitScenario() {
        const raw = document.getElementById('scenarioInput').value;
        try {
          const scenario = JSON.parse(raw);
          const response = await fetch('/api/recommend', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ scenario })
          });
          const data = await response.json();
          if (!response.ok) {
            throw new Error(data.detail || 'Request failed');
          }
          document.getElementById('result').textContent = JSON.stringify(data, null, 2);
        } catch (error) {
          document.getElementById('result').textContent = 'Error: ' + error.message;
        }
      }
    </script>
  </body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    return HTML_PAGE


@app.get("/api/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/api/recommend")
def recommend(payload: ScenarioInput) -> Dict[str, Any]:
    try:
        return engine.recommend(payload.scenario)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
