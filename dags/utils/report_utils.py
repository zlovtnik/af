"""Utility helpers for report DAG: DataFrame conversion, indicators, and report generation."""

from typing import Any, Dict, List, Optional, Tuple

import pandas as pd


def results_to_df(results: Optional[List[Tuple]], columns: List[str]) -> pd.DataFrame:
    """Convert SQL query results (list of tuples) into a pandas DataFrame.

    Args:
        results: List of row tuples returned by a DB hook/operator.
            If None, returns empty DF.
        columns: List of column names to apply.
    """
    if not results:
        return pd.DataFrame(columns=columns)
    return pd.DataFrame(results, columns=columns)


def compute_indicators_from_df(df: pd.DataFrame) -> Dict[str, Any]:
    """Compute example indicators from a dataframe with a 'revenue' column.

    Returns a dict with total, average, growth_rate, and an alert flag.
    """
    if df.empty or "revenue" not in df.columns:
        return {
            "total_revenue": 0,
            "avg_revenue": 0,
            "growth_rate": 0,
            "alert": "NoData",
        }

    total_revenue = float(df["revenue"].sum())
    avg_revenue = float(df["revenue"].mean())
    growth_rate = 0.0
    if len(df) > 1 and df["revenue"].iloc[0] != 0:
        growth_rate = float(
            (df["revenue"].iloc[-1] - df["revenue"].iloc[0])
            / df["revenue"].iloc[0]
            * 100
        )

    alert = "High" if avg_revenue > 1000 else "Normal"

    return {
        "total_revenue": total_revenue,
        "avg_revenue": avg_revenue,
        "growth_rate": growth_rate,
        "alert": alert,
    }


def generate_csv_report(
    indicators: Dict[str, Any],
    path: str,
    df: Optional[pd.DataFrame] = None,
    chart_path: Optional[str] = None,
) -> Dict[str, Optional[str]]:
    """Write indicators dict to CSV and optionally generate a chart from `df`.

    Returns a dict with keys 'csv' and 'chart' (chart is None if not generated).
    """
    report_df = pd.DataFrame([indicators])
    report_df.to_csv(path, index=False)

    saved_chart: Optional[str] = None
    if df is not None and "date" in df.columns and "revenue" in df.columns:
        try:
            import matplotlib.pyplot as plt

            tmp = df.copy()
            tmp["date"] = pd.to_datetime(tmp["date"])
            tmp = tmp.sort_values("date")

            # default chart path if not provided
            if chart_path is None:
                chart_path = str(path).rsplit(".", 1)[0] + ".png"

            plt.figure(figsize=(8, 4))
            plt.plot(tmp["date"], tmp["revenue"], marker="o")
            plt.title("Revenue over time")
            plt.xlabel("date")
            plt.ylabel("revenue")
            plt.tight_layout()
            plt.savefig(chart_path)
            plt.close()
            saved_chart = chart_path
        except Exception:
            # Don't fail report generation for chart errors; return csv only
            saved_chart = None

    return {"csv": path, "chart": saved_chart}
