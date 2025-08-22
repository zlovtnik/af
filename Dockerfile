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
ENV AIRFLOW__LOGGING__DAG_PROCESSOR_MANAGER_LOG_LOCATION=/app/logs/dag_processor_manager.log
ENV AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION=False
ENV AIRFLOW__LOGGING__LOGGING_LEVEL=INFO

# Set working directory
WORKDIR /app

# Install system dependencies including Oracle Instant Client
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    wget \
    unzip \
    libaio1 \
    && rm -rf /var/lib/apt/lists/*

# Install Oracle Instant Client
RUN mkdir -p /opt/oracle && \
    cd /opt/oracle && \
    wget https://download.oracle.com/otn_software/linux/instantclient/2340000/instantclient-basic-linux.x64-23.4.0.24.05.zip && \
    unzip instantclient-basic-linux.x64-23.4.0.24.05.zip && \
    rm instantclient-basic-linux.x64-23.4.0.24.05.zip && \
    echo /opt/oracle/instantclient_23_4 > /etc/ld.so.conf.d/oracle-instantclient.conf && \
    ldconfig

# Set Oracle environment variables
ENV LD_LIBRARY_PATH=/opt/oracle/instantclient_23_4:$LD_LIBRARY_PATH
ENV TNS_ADMIN=/opt/oracle/instantclient_23_4
ENV ORACLE_HOME=/opt/oracle/instantclient_23_4

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Create airflow user and set permissions before copying files
RUN useradd -m -s /bin/bash airflow && \
    mkdir -p /app/logs /app/logs/dag_processor_manager /app/logs/scheduler /app/dags && \
    chown -R airflow:airflow /app

# Copy the application code INCLUDING DAGs directly into the image
COPY --chown=airflow:airflow . .

# Ensure DAG files are properly copied and have correct permissions
RUN ls -la /app/dags/ && \
    chown -R airflow:airflow /app/dags && \
    chmod -R 755 /app/dags

# Create entrypoint script
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
# Ensure directories exist with proper permissions\n\
mkdir -p /app/logs/dag_processor_manager /app/logs/scheduler /app/dags\n\
chown -R airflow:airflow /app/logs\n\
chmod -R 755 /app/logs\n\
\n\
# Debug: List DAG files\n\
echo "DAG files in container:"\n\
ls -la /app/dags/\n\
\n\
# Initialize database if it does not exist\n\
if [ ! -f "/app/airflow.db" ]; then\n\
    echo "Initializing Airflow database..."\n\
    airflow db migrate\n\
    echo "Creating admin user..."\n\
    airflow users create \\\n\
        --username admin \\\n\
        --firstname Admin \\\n\
        --lastname User \\\n\
        --role Admin \\\n\
        --email admin@example.com \\\n\
        --password admin || true\n\
    \n\
    echo "Setting up Oracle connection..."\n\
    python /app/init_oracle_connection.py || true\n\
fi\n\
\n\
exec "$@"' > /app/entrypoint.sh && \
    chmod +x /app/entrypoint.sh && \
    chown airflow:airflow /app/entrypoint.sh

# Switch to airflow user
USER airflow

# Expose the webserver port
EXPOSE 8080

# Set entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]

# Default command
CMD ["airflow", "standalone"]
