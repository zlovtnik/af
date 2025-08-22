import os
import pathlib
import sys

import pandas as pd
import pytest

# Ensure project root is on sys.path so `dags` package is importable when running pytest
ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dags.utils.report_utils import (compute_indicators_from_df,
                                     generate_csv_report, results_to_df)


def test_results_to_df_empty():
    df = results_to_df(None, ["date", "revenue"])
    assert list(df.columns) == ["date", "revenue"]
    assert df.empty


def test_compute_indicators_from_df():
    df = pd.DataFrame({"date": ["2025-01-01", "2025-01-02"], "revenue": [100.0, 200.0]})
    indicators = compute_indicators_from_df(df)
    assert indicators["total_revenue"] == pytest.approx(300.0)
    assert indicators["avg_revenue"] == pytest.approx(150.0)
    assert indicators["growth_rate"] == pytest.approx(100.0)


def test_generate_csv_report(tmp_path):
    indicators = {
        "total_revenue": 10,
        "avg_revenue": 5,
        "growth_rate": 0,
        "alert": "Normal",
    }
    path = tmp_path / "report.csv"
    # Create small dataframe for charting
    df = pd.DataFrame({"date": ["2025-01-01", "2025-01-02"], "revenue": [10, 20]})
    returned = generate_csv_report(indicators, str(path), df=df)
    assert returned["csv"] == str(path)
    assert os.path.exists(returned["csv"])
    # Chart should be created alongside CSV
    assert returned["chart"] is not None
    assert os.path.exists(returned["chart"])
