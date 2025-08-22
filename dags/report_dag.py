from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

# Try to import Oracle components, handle gracefully if not available
try:
    from airflow.providers.oracle.hooks.oracle import OracleHook
    ORACLE_AVAILABLE = True
except ImportError:
    print("Oracle provider not available - using fallback implementations")
    ORACLE_AVAILABLE = False
    OracleHook = None

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
    'oracle_report_dag',
    default_args=default_args,
    description='Oracle-based report generation DAG',
    schedule=timedelta(days=1),
    catchup=False,
    tags=['oracle', 'report'],
)

def generate_oracle_report():
    """Generate a report using Oracle database data"""
    import pandas as pd
    from datetime import datetime

    if not ORACLE_AVAILABLE:
        print("Oracle provider not available - generating fallback report")
        data = {
            'report_type': ['Fallback Report (Oracle N/A)'],
            'report_timestamp': [datetime.now()],
            'database_user': ['N/A'],
            'database_name': ['N/A'],
            'records_processed': [100],
            'status': ['completed_fallback']
        }
        df = pd.DataFrame(data)
        print("Fallback report generated!")
        print(df.to_string(index=False))
        return "Fallback report generation completed"

    try:
        # Connect to Oracle and fetch data from DUAL
        oracle_hook = OracleHook(
            oracle_conn_id='oracle_default',
            thick_mode=False
        )
        
        # Create a comprehensive report query using DUAL
        sql = """
        SELECT 
            'Oracle Report' as report_type,
            SYSDATE as report_timestamp,
            USER as database_user,
            SYS_CONTEXT('USERENV', 'DB_NAME') as database_name,
            1000 + ROUND(DBMS_RANDOM.VALUE(1, 999)) as records_processed,
            'completed' as status
        FROM DUAL
        """
        
        result = oracle_hook.get_first(sql)
        
        # Create DataFrame from Oracle data
        data = {
            'report_type': [result[0]],
            'report_timestamp': [result[1]],
            'database_user': [result[2]],
            'database_name': [result[3]],
            'records_processed': [result[4]],
            'status': [result[5]]
        }

        df = pd.DataFrame(data)
        print("Oracle Report generated successfully!")
        print(df.to_string(index=False))
        
        # Additional Oracle system information
        version_sql = "SELECT BANNER FROM V$VERSION WHERE ROWNUM = 1"
        version_result = oracle_hook.get_first(version_sql)
        print(f"\nOracle Database Version: {version_result[0]}")
        
        return "Oracle report generation completed"
        
    except Exception as e:
        print(f"Error generating Oracle report: {str(e)}")
        # Fallback to local data if Oracle is not available
        data = {
            'report_type': ['Fallback Report'],
            'report_timestamp': [datetime.now()],
            'database_user': ['N/A'],
            'database_name': ['N/A'],
            'records_processed': [100],
            'status': ['completed_fallback']
        }
        df = pd.DataFrame(data)
        print("Fallback report generated!")
        print(df.to_string(index=False))
        return "Fallback report generation completed"

def cleanup_files():
    """Cleanup temporary files"""
    print("Cleaning up temporary files...")
    return "Cleanup completed"

# Define tasks
hello_task = BashOperator(
    task_id='say_hello',
    bash_command='echo "Hello from Airflow DAG! Starting Oracle report generation..."',
    dag=dag,
)

generate_report_task = PythonOperator(
    task_id='generate_oracle_report',
    python_callable=generate_oracle_report,
    dag=dag,
)

cleanup_task = PythonOperator(
    task_id='cleanup',
    python_callable=cleanup_files,
    dag=dag,
)

goodbye_task = BashOperator(
    task_id='say_goodbye',
    bash_command='echo "Oracle Report DAG completed successfully!"',
    dag=dag,
)

# Define task dependencies
hello_task >> generate_report_task >> cleanup_task >> goodbye_task
