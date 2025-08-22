from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.email import EmailOperator
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.utils import timezone

from dags.utils.report_utils import (compute_indicators_from_df,
                                     generate_csv_report, results_to_df)

default_args = {
    "owner": "airflow_user",
    "depends_on_past": False,
    "start_date": datetime(2025, 8, 21),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
}

dag = DAG(
    "sql_report_generation",
    default_args=default_args,
    description="Run SQL queries, compute indicators, and generate report",
    schedule_interval="@daily",
    catchup=False,
)


# Task 1: Run SQL Query (push results to XCom)
run_query = PostgresOperator(
    task_id="run_sql_query",
    postgres_conn_id="my_db",
    sql="""
        SELECT date, revenue FROM sales WHERE date >= '{{ ds }}' - INTERVAL '7 days';
    """,
    do_xcom_push=True,
    dag=dag,
)


def compute_indicators_task(**context):
    ti = context["ti"]
    query_results = ti.xcom_pull(task_ids="run_sql_query")
    # Convert to DataFrame; PostgresOperator typically returns list of tuples
    df = results_to_df(query_results, columns=["date", "revenue"])
    indicators = compute_indicators_from_df(df)
    ti.xcom_push(key="indicators", value=indicators)
    # Also push the dataframe rows for chart generation later
    ti.xcom_push(key="query_rows", value=query_results)
    return indicators


compute_task = PythonOperator(
    task_id="compute_indicators",
    python_callable=compute_indicators_task,
    provide_context=True,
    dag=dag,
)


def generate_report_task(**context):
    ti = context["ti"]
    indicators = ti.xcom_pull(key="indicators", task_ids="compute_indicators")
    # Use execution date in filename to avoid collisions
    exec_date = context.get("ds_nodash") or timezone.utcnow().strftime("%Y%m%d")
    report_path = f"/tmp/report_{exec_date}.csv"
    # reconstruct dataframe from xcom rows if available for charting
    query_rows = ti.xcom_pull(key="query_rows", task_ids="compute_indicators")
    df = results_to_df(query_rows, columns=["date", "revenue"])
    paths = generate_csv_report(indicators, report_path, df=df)
    ti.xcom_push(key="report_path", value=paths.get("csv"))
    ti.xcom_push(key="chart_path", value=paths.get("chart"))
    return paths


generate_task = PythonOperator(
    task_id="generate_report",
    python_callable=generate_report_task,
    provide_context=True,
    dag=dag,
)


# Optional: send report by email if you configure SMTP in Airflow
email_task = EmailOperator(
    task_id="send_report",
    to="you@example.com",
    subject="Daily SQL Report",
    html_content='Report generated. Indicators: {{ ti.xcom_pull(key="indicators") }}',
    files=['{{ ti.xcom_pull(key="report_path") }}'],
    dag=dag,
)


# Define dependencies
run_query >> compute_task >> generate_task >> email_task
