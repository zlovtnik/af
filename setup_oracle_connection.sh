#!/bin/bash

# Script to create Oracle connection in Airflow
# This should be run after the containers are up and running

echo "Setting up Oracle connection in Airflow..."

# Wait for Airflow to be ready
sleep 30

# Create Oracle connection using Airflow CLI
docker exec airflow_dev airflow connections add \
    --conn-id oracle_default \
    --conn-type oracle \
    --conn-host oracle \
    --conn-port 1521 \
    --conn-login system \
    --conn-password OraclePassword123 \
    --conn-extra '{"service_name": "FREEPDB1"}'

echo "Oracle connection created successfully!"

# Test the connection
docker exec airflow_dev airflow connections test oracle_default

echo "Connection test completed!"
