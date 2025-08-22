#!/bin/bash
# init_oracle_connection.py - Python script to create Oracle connection

import os
from airflow.models import Connection
from airflow import settings

def create_oracle_connection():
    """Create Oracle database connection"""
    try:
        # Get session
        session = settings.Session()
        
        # Check if connection already exists
        existing_conn = session.query(Connection).filter(Connection.conn_id == 'oracle_default').first()
        
        if existing_conn:
            print("Oracle connection already exists, updating...")
            session.delete(existing_conn)
        
        # Create new connection
        oracle_conn = Connection(
            conn_id='oracle_default',
            conn_type='oracle',
            host=os.getenv('ORACLE_HOST', 'oracle'),
            port=int(os.getenv('ORACLE_PORT', '1521')),
            login=os.getenv('ORACLE_USER', 'system'),
            password=os.getenv('ORACLE_PASSWORD', 'OraclePassword123'),
            extra='{"service_name": "FREEPDB1"}'
        )
        
        # Add to session and commit
        session.add(oracle_conn)
        session.commit()
        session.close()
        
        print("Oracle connection created successfully!")
        return True
        
    except Exception as e:
        print(f"Error creating Oracle connection: {str(e)}")
        return False

if __name__ == "__main__":
    create_oracle_connection()
