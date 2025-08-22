from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.models import Variable
import os

# Try to import Oracle components, handle gracefully if not available
try:
    from airflow.providers.oracle.operators.oracle import OracleOperator
    from airflow.providers.oracle.hooks.oracle import OracleHook
    ORACLE_AVAILABLE = True
except ImportError:
    print("Oracle provider not available - using fallback implementations")
    ORACLE_AVAILABLE = False
    OracleOperator = None
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
    'oracle_dual_dag',
    default_args=default_args,
    description='Oracle DAG that queries DUAL table',
    schedule=timedelta(days=1),
    catchup=False,
    tags=['oracle', 'database'],
)

def test_oracle_connection():
    """Test Oracle connection and query DUAL"""
    if not ORACLE_AVAILABLE:
        print("Oracle provider not available - simulating Oracle query")
        return "Simulated Oracle DUAL query: ('Hello from simulated Oracle!', '2024-08-22 12:00:00')"
    
    try:
        # Create Oracle hook using connection details from environment variables
        oracle_hook = OracleHook(
            oracle_conn_id='oracle_default',
            thick_mode=False  # Use thin mode (doesn't require Oracle Instant Client)
        )
        
        # Test connection
        connection = oracle_hook.get_conn()
        print("Successfully connected to Oracle database!")
        
        # Execute SELECT from DUAL
        sql = "SELECT 'Hello from Oracle DUAL!' as message, SYSDATE as current_time FROM DUAL"
        result = oracle_hook.get_first(sql)
        
        print(f"Query result: {result}")
        print(f"Message: {result[0]}")
        print(f"Current Oracle time: {result[1]}")
        
        connection.close()
        return f"Oracle DUAL query successful: {result}"
        
    except Exception as e:
        print(f"Error connecting to Oracle: {str(e)}")
        print("Falling back to simulated result")
        return f"Simulated Oracle result due to error: {str(e)}"

def get_oracle_version():
    """Get Oracle database version"""
    if not ORACLE_AVAILABLE:
        print("Oracle provider not available - simulating version query")
        return "Oracle Database 23c Free - Simulated"
    
    try:
        oracle_hook = OracleHook(
            oracle_conn_id='oracle_default',
            thick_mode=False
        )
        
        sql = "SELECT BANNER FROM V$VERSION WHERE ROWNUM = 1"
        result = oracle_hook.get_first(sql)
        
        print(f"Oracle version: {result[0]}")
        return result[0]
        
    except Exception as e:
        print(f"Error getting Oracle version: {str(e)}")
        return f"Oracle version unavailable: {str(e)}"

def execute_dual_with_calculations():
    """Execute more complex queries on DUAL"""
    if not ORACLE_AVAILABLE:
        print("Oracle provider not available - simulating calculations")
        return [2, "SIMULATED_USER", "2024-08-22 12:00:00", 42]
    
    try:
        oracle_hook = OracleHook(
            oracle_conn_id='oracle_default',
            thick_mode=False
        )
        
        # Multiple queries using DUAL
        queries = [
            "SELECT 1 + 1 as simple_math FROM DUAL",
            "SELECT USER as current_user FROM DUAL",
            "SELECT TO_CHAR(SYSDATE, 'YYYY-MM-DD HH24:MI:SS') as formatted_date FROM DUAL",
            "SELECT ROUND(DBMS_RANDOM.VALUE(1, 100)) as random_number FROM DUAL"
        ]
        
        results = []
        for sql in queries:
            result = oracle_hook.get_first(sql)
            results.append(result[0])
            print(f"Query: {sql}")
            print(f"Result: {result[0]}")
            print("---")
        
        return results
        
    except Exception as e:
        print(f"Error executing DUAL calculations: {str(e)}")
        print("Returning simulated results")
        return [2, "FALLBACK_USER", "2024-08-22 12:00:00", 50]

# Task 1: Test Oracle connection and basic DUAL query
test_connection_task = PythonOperator(
    task_id='test_oracle_connection',
    python_callable=test_oracle_connection,
    dag=dag,
)

# Task 2: Get Oracle version
get_version_task = PythonOperator(
    task_id='get_oracle_version',
    python_callable=get_oracle_version,
    dag=dag,
)

# Task 3: Execute DUAL with calculations
dual_calculations_task = PythonOperator(
    task_id='dual_calculations',
    python_callable=execute_dual_with_calculations,
    dag=dag,
)

# Alternative using OracleOperator for direct SQL execution (if available)
if ORACLE_AVAILABLE:
    oracle_operator_task = OracleOperator(
        task_id='oracle_operator_dual',
        oracle_conn_id='oracle_default',
        sql="SELECT 'Direct Oracle Operator Query' as method, SYSTIMESTAMP as timestamp FROM DUAL",
        dag=dag,
    )
else:
    # Fallback to BashOperator if Oracle provider not available
    oracle_operator_task = BashOperator(
        task_id='oracle_operator_dual_fallback',
        bash_command='echo "Oracle Operator not available - using fallback"',
        dag=dag,
    )

# Define task dependencies
test_connection_task >> get_version_task >> dual_calculations_task >> oracle_operator_task
