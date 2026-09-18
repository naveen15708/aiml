const form = document.querySelector("#assessment-form");
const result = document.querySelector("#result");
const error = document.querySelector("#error");

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  error.textContent = "";
  const data = Object.fromEntries(new FormData(form).entries());
  try {
    const response = await fetch("/api/assess", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(data),
    });
    const body = await response.json();
    if (!response.ok) throw new Error(body.error || "Unable to assess application");
    render(body);
  } catch (exception) {
    error.textContent = exception.message;
  }
});

function render(data) {
  const confidence = Math.round(data.confidence * 100);
  const factors = data.factors.map((factor) => {
    const positive = factor.direction === "supports";
    const width = Math.max(8, Math.round(factor.quality * 100));
    return `<li><div class="factor-top"><span>${factor.label}</span><strong class="${positive ? "positive" : "negative"}">${positive ? "+" : "−"}${Math.abs(Math.round(factor.impact * 100))}</strong></div><div class="bar"><i class="${positive ? "positive-bg" : "negative-bg"}" style="width:${width}%"></i></div><small>${factor.detail} · ${positive ? "supports" : "weakens"} the recommendation</small></li>`;
  }).join("");
  result.innerHTML = `<div class="section-heading"><span>02</span><h2>Assessment result</h2></div><div class="decision"><div><p class="label">RECOMMENDATION</p><h3>${data.recommendation}</h3></div><div class="confidence"><b>${confidence}%</b><span>confidence</span></div></div><p class="summary">${data.summary}</p><div class="section-heading factors-heading"><span>03</span><h2>What influenced it</h2></div><ul class="factors">${factors}</ul><details><summary>How this model works</summary><p>${data.methodology.confidence_note} Each factor is normalized and combined with a published weight; no hidden features are used.</p></details>`;
}
