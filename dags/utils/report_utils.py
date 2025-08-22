"""Utility helpers for report DAG: DataFrame conversion, indicators, and report generation."""

from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime

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
    if df.empty:
        return {
            'total_records': 0,
            'total_revenue': 0,
            'average_revenue': 0,
            'max_revenue': 0,
            'min_revenue': 0
        }

    indicators = {
        'total_records': len(df),
        'computation_date': datetime.now().isoformat(),
    }

    # If revenue column exists, compute revenue indicators
    if 'revenue' in df.columns:
        revenue_col = pd.to_numeric(df['revenue'], errors='coerce')
        indicators.update({
            'total_revenue': float(revenue_col.sum()),
            'average_revenue': float(revenue_col.mean()),
            'max_revenue': float(revenue_col.max()),
            'min_revenue': float(revenue_col.min())
        })

    return indicators


def generate_csv_report(
    indicators: Dict[str, Any],
    path: str,
    df: Optional[pd.DataFrame] = None,
    chart_path: Optional[str] = None,
) -> Dict[str, Optional[str]]:
    """Write indicators dict to CSV and optionally generate a chart from `df`.

    Returns a dict with keys 'csv' and 'chart' (chart is None if not generated).
    """
    # Create indicators DataFrame and save as CSV
    indicators_df = pd.DataFrame([indicators])
    indicators_df.to_csv(path, index=False)

    paths = {'csv': path}

    # Generate chart if DataFrame is provided and has revenue data
    if df is not None and not df.empty and 'revenue' in df.columns:
        chart_path = path.replace('.csv', '_chart.png')

        try:
            import matplotlib.pyplot as plt

            plt.figure(figsize=(10, 6))

            # Convert date column if it exists
            if 'date' in df.columns:
                df_plot = df.copy()
                df_plot['date'] = pd.to_datetime(df_plot['date'])
                df_plot = df_plot.sort_values('date')

                plt.plot(df_plot['date'], df_plot['revenue'], marker='o')
                plt.title('Revenue Over Time')
                plt.xlabel('Date')
                plt.ylabel('Revenue')
                plt.xticks(rotation=45)
            else:
                plt.bar(range(len(df)), df['revenue'])
                plt.title('Revenue Distribution')
                plt.xlabel('Record Index')
                plt.ylabel('Revenue')

            plt.tight_layout()
            plt.savefig(chart_path, dpi=150, bbox_inches='tight')
            plt.close()

            paths['chart'] = chart_path

        except Exception as e:
            print(f"Warning: Could not generate chart: {e}")

    return paths


def validate_data(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Validate the data and return validation results.

    Args:
        df: pandas DataFrame to validate

    Returns:
        Dictionary with validation results
    """
    validation_results = {
        'is_valid': True,
        'errors': [],
        'warnings': []
    }

    if df.empty:
        validation_results['errors'].append('DataFrame is empty')
        validation_results['is_valid'] = False

    # Check for required columns
    required_columns = ['date', 'revenue']
    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        validation_results['warnings'].append(f'Missing columns: {missing_columns}')

    # Check for null values in revenue
    if 'revenue' in df.columns:
        null_revenue_count = df['revenue'].isnull().sum()
        if null_revenue_count > 0:
            validation_results['warnings'].append(f'Found {null_revenue_count} null revenue values')

    return validation_results
