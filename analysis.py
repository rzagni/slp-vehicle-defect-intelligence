import pandas as pd
from typing import Dict, List


def analyze_complaints(complaints: List[Dict]) -> Dict:
    if not complaints:
        return {
            "component_counts": pd.DataFrame(),
            "severity": {},
            "state_counts": pd.DataFrame(),
            "yearly_trend": pd.DataFrame(),
            "component_severity": pd.DataFrame(),
            "case_strength_score": 0,
        }

    df = pd.DataFrame(complaints)

    # -----------------------
    # Data Cleaning
    # -----------------------
    df["component"] = df["component"].fillna("UNKNOWN")
    df["state"] = df["state"].fillna("UNKNOWN")

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["year"] = df["date"].dt.year

    # Ensure numeric flags
    for col in ["crash", "injury", "fire", "death"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    # -----------------------
    # Component Aggregation
    # -----------------------
    component_counts = (
        df.groupby("component")
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
    )

    # -----------------------
    # Severity Aggregation
    # -----------------------
    total_complaints = len(df)
    crashes = int(df["crash"].sum())
    injuries = int(df["injury"].sum())
    fires = int(df["fire"].sum())
    deaths = int(df["death"].sum())

    severity = {
        "total_complaints": total_complaints,
        "crashes": crashes,
        "injuries": injuries,
        "fires": fires,
        "deaths": deaths,
    }

    # -----------------------
    # Case Strength Score
    # -----------------------
    case_strength_score = (
        (5 * injuries) +
        (3 * crashes) +
        (2 * fires) +
        (10 * deaths) +
        (0.01 * total_complaints)
    )

    # -----------------------
    # Component-Level Severity
    # -----------------------
    component_severity = (
        df.groupby("component")[["crash", "injury", "fire", "death"]]
        .sum()
        .reset_index()
    )

    # -----------------------
    # Geographic Distribution
    # -----------------------
    state_counts = (
        df.groupby("state")
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
    )

    # -----------------------
    # Trend Over Time
    # -----------------------
    yearly_trend = (
        df.groupby("year")
        .size()
        .reset_index(name="count")
        .sort_values("year")
    )

    return {
        "component_counts": component_counts,
        "severity": severity,
        "state_counts": state_counts,
        "yearly_trend": yearly_trend,
        "component_severity": component_severity,
        "case_strength_score": round(case_strength_score, 2),
    }