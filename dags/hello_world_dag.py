from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

def simple_task():
    print("Hello from your first DAG!")
    return "Task completed successfully"

def another_task():
    print("This is a second task")
    return "Second task completed"

# Create the DAG
with DAG(
    'hello_world_dag',
    description='A simple hello world DAG', schedule ='@daily',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['example', 'hello'],
    default_args={
        'owner': 'admin',
        'retries': 1,
        'retry_delay': timedelta(minutes=5),
    }
) as dag:

    # Task 1: Say hello
    hello = BashOperator(
        task_id='say_hello',
        bash_command='echo "Hello Airflow!"'
    )

    # Task 2: Python task
    python_task = PythonOperator(
        task_id='python_task',
        python_callable=simple_task
    )

    # Task 3: Another Python task
    second_python_task = PythonOperator(
        task_id='second_python_task',
        python_callable=another_task
    )

    # Task 4: Final message
    goodbye = BashOperator(
        task_id='say_goodbye',
        bash_command='echo "DAG completed successfully!"'
    )

    # Set task dependencies
    hello >> python_task >> second_python_task >> goodbye
