import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import pytest

from src.batch_tlf_efficiency import efficiency_comparison
from src.checksum_validation import compute_checksum, validate_against_baseline
from src.audit_trail import record_execution, traceability_report, AUDIT_LOG
from src.risk_assessment import assess_risks, risk_tier


def test_batch_efficiency_shows_real_improvement():
    result = efficiency_comparison()
    assert 0 < result["efficiency_improvement_pct"] < 100


def test_checksum_detects_no_change_correctly():
    df = pd.DataFrame({"x": [1, 2, 3]})
    h = compute_checksum(df)
    assert validate_against_baseline(df, h)["unchanged"] is True


def test_checksum_detects_real_change():
    df = pd.DataFrame({"x": [1, 2, 3]})
    h = compute_checksum(df)
    df2 = df.copy()
    df2.loc[0, "x"] = 999
    assert validate_against_baseline(df2, h)["unchanged"] is False


def test_audit_trail_records_are_fully_traceable():
    AUDIT_LOG.clear()
    df = pd.DataFrame({"x": [1, 2, 3]})
    record_execution("test_macro", "TEST", "GENERATE", None, df)
    report = traceability_report()
    assert report["pct_fully_traceable"] == 100.0


def test_risk_tier_boundaries():
    assert risk_tier(20) == "High"
    assert risk_tier(10) == "Medium"
    assert risk_tier(2) == "Low"


def test_all_four_components_assessed():
    risks = assess_risks()
    assert len(risks) == 4
    assert set(risks["risk_tier"]) <= {"High", "Medium", "Low"}


def test_checksum_validation_macro_rated_highest_impact():
    """The data-integrity control itself should be rated the highest
    impact -- a real risk-assessment sanity check, not an arbitrary one."""
    risks = assess_risks()
    checksum_row = risks[risks["component"].str.contains("Checksum")].iloc[0]
    assert checksum_row["impact"] == risks["impact"].max()
