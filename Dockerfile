# Use the official Python 3.11 image (Python 3.13 has compatibility issues with Airflow)
FROM python:3.11-slim

# Set environment variables
ENV AIRFLOW_HOME=/app
ENV PYTHONPATH=/app
ENV AIRFLOW__CORE__DAGS_FOLDER=/app/dags
ENV AIRFLOW__CORE__LOAD_EXAMPLES=False
ENV AIRFLOW__WEBSERVER__EXPOSE_CONFIG=True
ENV AIRFLOW__CORE__EXECUTOR=LocalExecutor
ENV AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=sqlite:////app/airflow.db
ENV AIRFLOW__LOGGING__BASE_LOG_FOLDER=/app/logs
ENV AIRFLOW__LOGGING__DAG_PROCESSOR_MANAGER_LOG_LOCATION=/app/logs/dag_processor_manager/dag_processor_manager.log

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Create airflow user and set permissions
RUN useradd -m -s /bin/bash airflow && \
    mkdir -p /app/logs /app/logs/dag_processor_manager && \
    chown -R airflow:airflow /app

# Switch to airflow user
USER airflow

# Create entrypoint script
RUN echo '#!/bin/bash\n\
# Initialize database if it does not exist\n\
if [ ! -f "/app/airflow.db" ]; then\n\
    echo "Initializing Airflow database..."\n\
    airflow db migrate\n\
    airflow users create \\\n\
        --username admin \\\n\
        --firstname Admin \\\n\
        --lastname User \\\n\
        --role Admin \\\n\
        --email admin@example.com \\\n\
        --password admin\n\
fi\n\
exec "$@"' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# Expose the webserver port
EXPOSE 8080

# Set entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]

# Default command
CMD ["airflow", "standalone"]
