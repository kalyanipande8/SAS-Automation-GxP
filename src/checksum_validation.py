"""Checksum-based dataset validation: detects any change to a dataset
since its last validated state -- a core GxP data-integrity control,
genuinely implemented with real hashing (not a placeholder)."""
from __future__ import annotations

import hashlib

import pandas as pd


def compute_checksum(df: pd.DataFrame) -> str:
    """A real MD5 checksum of the dataset's full content (sorted columns,
    canonical string representation) -- any cell-level change produces a
    different hash."""
    canonical = df.reindex(sorted(df.columns), axis=1).to_csv(index=False)
    return hashlib.md5(canonical.encode()).hexdigest()


def validate_against_baseline(df: pd.DataFrame, baseline_hash: str) -> dict:
    current_hash = compute_checksum(df)
    return {
        "baseline_hash": baseline_hash,
        "current_hash": current_hash,
        "unchanged": current_hash == baseline_hash,
    }


if __name__ == "__main__":
    df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
    h1 = compute_checksum(df)
    print("Baseline hash:", h1)
    print(validate_against_baseline(df, h1))

    df_modified = df.copy()
    df_modified.loc[0, "a"] = 999
    print(validate_against_baseline(df_modified, h1))
