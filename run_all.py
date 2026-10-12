"""End-to-end: run the batch-TLF efficiency benchmark, exercise the
checksum validation + audit trail, and run the GAMP5 risk assessment."""
import json
import os

import numpy as np
import pandas as pd

from src.batch_tlf_efficiency import efficiency_comparison
from src.checksum_validation import compute_checksum, validate_against_baseline
from src.audit_trail import record_execution, traceability_report, AUDIT_LOG
from src.risk_assessment import assess_risks

os.makedirs("data", exist_ok=True)
os.makedirs("results", exist_ok=True)

print("=== Batch TLF generation efficiency benchmark ===")
efficiency = efficiency_comparison()
print(efficiency)

print("\n=== Checksum-based dataset validation ===")
rng = np.random.default_rng(89)
df = pd.DataFrame({"usubjid": [f"S{i:03d}" for i in range(100)], "age": rng.integers(18, 90, 100)})
baseline_hash = compute_checksum(df)
record_execution("gen_summary_table", "ADSL", "GENERATE", None, df)

df_changed = df.copy()
df_changed.loc[0, "age"] = 999
validation_unchanged = validate_against_baseline(df, baseline_hash)
validation_changed = validate_against_baseline(df_changed, baseline_hash)
record_execution("validate_dataset_checksum", "ADSL", "VALIDATE", df, df_changed)
print("Unchanged dataset check:", validation_unchanged)
print("Changed dataset check:  ", validation_changed)

print("\n=== GxP audit trail traceability ===")
traceability = traceability_report()
print(traceability)

print("\n=== GAMP5 risk assessment ===")
risks = assess_risks()
print(risks[["component", "likelihood", "impact", "risk_score", "risk_tier"]])
risks.to_csv("results/risk_assessment.csv", index=False)

summary = {
    "efficiency_improvement_pct": efficiency["efficiency_improvement_pct"],
    "checksum_correctly_detects_unchanged_data": validation_unchanged["unchanged"],
    "checksum_correctly_detects_changed_data": not validation_changed["unchanged"],
    "audit_trail_pct_fully_traceable": traceability["pct_fully_traceable"],
    "n_risk_components_assessed": len(risks),
    "highest_risk_component": risks.sort_values("risk_score", ascending=False).iloc[0]["component"],
}
with open("results/summary.json", "w") as f:
    json.dump(summary, f, indent=2, default=str)

print("\n=== Summary ===")
print(json.dumps(summary, indent=2, default=str))
