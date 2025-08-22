from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
dag = DAG(
    'simple_report_dag',
    default_args=default_args,
    description='A simple report generation DAG',
    schedule=timedelta(days=1),
    catchup=False,
    tags=['example', 'report'],
)

def generate_simple_report():
    """Generate a simple report"""
    import pandas as pd
    from datetime import datetime

    # Create sample data
    data = {
        'date': [datetime.now().strftime('%Y-%m-%d')],
        'records_processed': [100],
        'status': ['completed']
    }

    df = pd.DataFrame(data)
    print("Report generated successfully!")
    print(df.to_string(index=False))
    return "Report generation completed"

def cleanup_files():
    """Cleanup temporary files"""
    print("Cleaning up temporary files...")
    return "Cleanup completed"

# Define tasks
hello_task = BashOperator(
    task_id='say_hello',
    bash_command='echo "Hello from Airflow DAG! Starting report generation..."',
    dag=dag,
)

generate_report_task = PythonOperator(
    task_id='generate_report',
    python_callable=generate_simple_report,
    dag=dag,
)

cleanup_task = PythonOperator(
    task_id='cleanup',
    python_callable=cleanup_files,
    dag=dag,
)

goodbye_task = BashOperator(
    task_id='say_goodbye',
    bash_command='echo "Report DAG completed successfully!"',
    dag=dag,
)

# Define task dependencies
hello_task >> generate_report_task >> cleanup_task >> goodbye_task
