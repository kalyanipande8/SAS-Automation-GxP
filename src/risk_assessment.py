"""GAMP5-style (Good Automated Manufacturing Practice) risk categorization
for each automated component: likelihood x impact on a 1-5 scale,
producing a real risk score and tier, used to prioritize validation depth
(the standard risk-based validation approach GxP guidance recommends)."""
from __future__ import annotations

import pandas as pd

COMPONENTS = [
    {"component": "Batch TLF generation macro", "likelihood": 3, "impact": 4,
     "rationale": "Moderate chance of a spec error; high impact since it affects every generated output"},
    {"component": "Checksum dataset validation macro", "likelihood": 2, "impact": 5,
     "rationale": "Low chance of a hashing bug; very high impact since this is the data-integrity control itself"},
    {"component": "Audit record macro", "likelihood": 2, "impact": 3,
     "rationale": "Low chance of logging failure; moderate impact (traceability gap, not data corruption)"},
    {"component": "Risk-scoring macro", "likelihood": 1, "impact": 2,
     "rationale": "Low chance of arithmetic error; low impact (informs prioritization, doesn't touch data)"},
]


def risk_tier(score: int) -> str:
    if score >= 15:
        return "High"
    if score >= 8:
        return "Medium"
    return "Low"


def assess_risks(components: list[dict] = COMPONENTS) -> pd.DataFrame:
    rows = []
    for c in components:
        score = c["likelihood"] * c["impact"]
        rows.append({**c, "risk_score": score, "risk_tier": risk_tier(score)})
    return pd.DataFrame(rows)


if __name__ == "__main__":
    print(assess_risks())
