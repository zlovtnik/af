# Apache Airflow with Oracle Database Project

A Docker-based Apache Airflow development environment with Oracle Database integration using Oracle AI free image.

## Prerequisites

- Docker and Docker Compose installed on your system
- Make utility (available on macOS/Linux by default)
- At least 8GB of RAM (Oracle database requires significant memory)

## Oracle Database Features

This project includes:
- Oracle Database Free 23c container
- Airflow DAGs that connect to Oracle and query DUAL table
- Automatic Oracle connection setup
- Sample Oracle-based reporting DAG

## Quick Start

### Initial Setup
```bash
# Clone the repository and navigate to the project directory
cd /path/to/your/af/project

# Build Docker image and initialize Airflow database with Oracle
make setup
```

### Start Airflow
```bash
# Start Airflow in standalone mode (detached)
make up

# Access Airflow web interface at: http://localhost:8080
# Default credentials: admin / admin
```

### Stop Airflow
```bash
# Stop all containers
make down
```

## Available Commands

Run `make help` to see all available commands, or use any of the commands below:

### Docker Management
- `make build` - Build the Docker image
- `make up` - Start Airflow in standalone mode (detached)
- `make down` - Stop and remove containers
- `make logs` - Show container logs (follow mode)
- `make shell` - Open a shell in the running container
- `make restart` - Restart the Airflow container
- `make status` - Show container status

### Development & Testing
- `make test` - Run all tests in container
- `make test-watch` - Run tests in watch mode
- `make lint` - Run linting checks (flake8) in container
- `make format` - Format code with black and isort
- `make clean` - Clean up Docker resources and cache files

### Airflow Operations
- `make airflow-start` - Start Airflow (alias for `up`)
- `make airflow-stop` - Stop Airflow (alias for `down`)
- `make airflow-init` - Initialize Airflow database in container
- `make airflow-test` - Test DAG syntax and imports
- `make airflow-list` - List all DAGs
- `make airflow-web` - Show Airflow webserver access info

### Database Management
- `make db-migrate` - Run database migrations
- `make db-reset` - Reset Airflow database (WARNING: destructive)

### Utilities
- `make check-deps` - Check for dependency issues
- `make setup` - Complete development environment setup

### Oracle Database Operations
- Oracle Database runs on port 1521 (database) and 5500 (Enterprise Manager)
- Default connection: `system/OraclePassword123@localhost:1521/FREEPDB1`
- The setup script automatically creates the Airflow connection `oracle_default`
- To manually set up Oracle connection: `./setup_oracle_connection.sh`

```

## Project Structure

```
├── Dockerfile              # Docker image definition
├── docker-compose.yml      # Docker Compose configuration
├── Makefile                # Development commands
├── requirements.txt        # Python dependencies
├── dags/                   # Airflow DAGs directory
│   ├── report_dag.py      # Example DAG
│   └── utils/             # DAG utilities
│       └── report_utils.py
├── tests/                  # Test files
│   └── test_report_utils.py
└── README.md              # This file
```

## Development Workflow

### 1. Making Changes to DAGs
Your `dags/` and `tests/` directories are mounted as volumes, so changes are reflected immediately in the running container.

### 2. Running Tests
```bash
# Run all tests
make test

# Run tests in watch mode (reruns on file changes)
make test-watch
```

### 3. Code Quality
```bash
# Check code style and errors
make lint

# Auto-format code
make format
```

### 4. Debugging
```bash
# View real-time logs
make logs

# Access container shell for debugging
make shell

# Check if DAGs are valid
make airflow-test

# List all available DAGs
make airflow-list
```

## Configuration

### Environment Variables
The Docker setup uses the following key environment variables (defined in Dockerfile):

- `AIRFLOW_HOME=/app` - Airflow home directory
- `AIRFLOW__CORE__DAGS_FOLDER=/app/dags` - DAGs location
- `AIRFLOW__CORE__LOAD_EXAMPLES=False` - Disable example DAGs
- `AIRFLOW__CORE__EXECUTOR=LocalExecutor` - Use Local Executor
- `AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=sqlite:////app/airflow.db` - SQLite database

### Default Credentials
The Airflow system generates a random password for the admin user on first initialization. To find your password:

1. **Check the generated password file**:
```bash
cat simple_auth_manager_passwords.json.generated
```

2. **Your credentials will be**:
   - **Username**: admin  
   - **Password**: [check the generated file - it will be a random string like `Hp3YkbakNbxFt7py`]
   - **Web Interface**: http://localhost:8080

Note: The password is randomly generated each time Airflow initializes, so it will be different for each setup.

## Troubleshooting

### Container Issues
```bash
# Check container status
make status

# View logs for errors
make logs

# Restart containers
make restart

# Clean up and start fresh
make clean
make setup
```

### DAG Issues
```bash
# Test DAG imports
make airflow-test

# Check DAG list
make airflow-list

# Access container to debug
make shell
```

### Permission Issues
If you encounter permission issues, the Docker setup runs as the `airflow` user inside the container, which should handle most permission scenarios automatically.

## Dependencies

The project uses the following main dependencies (see `requirements.txt`):

- **apache-airflow>=2.10.0** - Main Airflow package
- **apache-airflow-providers-postgres>=5.0.0** - PostgreSQL provider
- **pandas>=1.5.0** - Data processing
- **pytest>=7.0.0** - Testing framework
- **black>=23.0.0** - Code formatter
- **isort>=5.0.0** - Import sorter
- **flake8>=6.0.0** - Linter

## Contributing

1. Make your changes to DAGs or utility code
2. Run tests: `make test`
3. Check code quality: `make lint`
4. Format code: `make format`
5. Test DAG syntax: `make airflow-test`

## Migration from Local Setup

If you were previously using a local Python virtual environment:

1. Remove the old `.venv` directory: `rm -rf .venv`
2. Clean up local Python cache: `make clean`
3. Run the new setup: `make setup`
4. Start Airflow: `make up`

The new Docker-based setup eliminates Python version compatibility issues and provides a consistent development environment.
