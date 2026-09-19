const form = document.querySelector("#assessment-form");
const result = document.querySelector("#result");
const error = document.querySelector("#error");

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  error.textContent = "";
  try {
    render(assess(Object.fromEntries(new FormData(form).entries())));
  } catch (exception) {
    error.textContent = exception.message;
  }
});

function number(data, key) {
  const value = Number(data[key]);
  if (!Number.isFinite(value) || value < 0) throw new Error(`${key} must be a valid non-negative number`);
  return value;
}

function clamp(value, lower = 0, upper = 1) {
  return Math.max(lower, Math.min(upper, value));
}

function quality(value, low, high) {
  return clamp((value - low) / (high - low));
}

function riskQuality(value, good, bad) {
  return clamp((bad - value) / (bad - good));
}

function assess(data) {
  const creditScore = number(data, "credit_score");
  const debtToIncome = number(data, "debt_to_income");
  const annualIncome = number(data, "annual_income");
  const cashReserves = number(data, "cash_reserves");
  const businessYears = number(data, "business_years");
  const requestedAmount = number(data, "requested_amount");
  if (creditScore < 300 || creditScore > 850) throw new Error("credit_score must be between 300 and 850");
  if (debtToIncome > 100) throw new Error("debt_to_income must be between 0 and 100");
  if (annualIncome === 0) throw new Error("annual_income must be greater than zero");

  const loanToIncome = requestedAmount / annualIncome;
  const values = {
    credit_score: quality(creditScore, 300, 850),
    debt_to_income: riskQuality(debtToIncome, 20, 60),
    annual_income: quality(annualIncome, 20000, 250000),
    cash_reserves: quality(cashReserves, 0, 100000),
    business_years: quality(businessYears, 0, 10),
    loan_to_income: riskQuality(loanToIncome, 0.15, 1),
  };
  const details = {
    credit_score: `${creditScore.toFixed(0)} credit score`,
    debt_to_income: `${debtToIncome.toFixed(1)}% debt-to-income`,
    annual_income: `$${annualIncome.toLocaleString()} annual income`,
    cash_reserves: `$${cashReserves.toLocaleString()} cash reserves`,
    business_years: `${businessYears.toFixed(1)} years in business`,
    loan_to_income: `${loanToIncome.toFixed(2)}x requested loan to income`,
  };
  const features = [
    ["credit_score", "Credit score", 0.30],
    ["debt_to_income", "Debt-to-income ratio", 0.20],
    ["annual_income", "Annual income", 0.20],
    ["cash_reserves", "Cash reserves", 0.15],
    ["business_years", "Years in business", 0.10],
    ["loan_to_income", "Requested loan vs income", 0.05],
  ];
  let score = 0;
  const factors = features.map(([key, label, weight]) => {
    const impact = (values[key] - 0.5) * weight;
    score += impact;
    return {key, label, impact, quality: values[key], direction: impact >= 0 ? "supports" : "weakens", detail: details[key]};
  }).sort((left, right) => Math.abs(right.impact) - Math.abs(left.impact));
  const probability = 1 / (1 + Math.exp(-8 * score));
  return {
    recommendation: probability >= 0.65 ? "Likely eligible" : probability >= 0.40 ? "Needs review" : "Higher risk",
    confidence: Math.min(0.96, 0.55 + Math.abs(probability - 0.5) * 0.8),
    summary: "The strongest positive and negative factors are shown below. This is a pre-screening aid, not a lending decision.",
    factors,
    methodology: {confidence_note: "Confidence reflects score separation from the review boundary and is not a probability of repayment."},
  };
}

function render(data) {
  const confidence = Math.round(data.confidence * 100);
  const factors = data.factors.map((factor) => {
    const positive = factor.direction === "supports";
    const width = Math.max(8, Math.round(factor.quality * 100));
    return `<li><div class="factor-top"><span>${factor.label}</span><strong class="${positive ? "positive" : "negative"}">${positive ? "+" : "−"}${Math.abs(Math.round(factor.impact * 100))}</strong></div><div class="bar"><i class="${positive ? "positive-bg" : "negative-bg"}" style="width:${width}%"></i></div><small>${factor.detail} · ${positive ? "supports" : "weakens"} the recommendation</small></li>`;
  }).join("");
  result.innerHTML = `<div class="section-heading"><span>02</span><h2>Assessment result</h2></div><div class="decision"><div><p class="label">RECOMMENDATION</p><h3>${data.recommendation}</h3></div><div class="confidence"><b>${confidence}%</b><span>confidence</span></div></div><p class="summary">${data.summary}</p><div class="section-heading factors-heading"><span>03</span><h2>What influenced it</h2></div><ul class="factors">${factors}</ul><details><summary>How this model works</summary><p>${data.methodology.confidence_note} Each factor is normalized and combined with a published weight; no hidden features are used.</p></details>`;
}
