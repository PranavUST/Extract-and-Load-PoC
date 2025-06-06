# File Structure
REST_API_Implementation/
├── config/
│   └── api_config.yaml
│   └── ftp_config.yaml
├── data/
│   └── output.csv
│   └── scheduler_state.json
├── ftp_downloads
├── sample_api/
│   ├── __init__.py
│   └── app.py
│   └── posts.json
├── scripts/
│   └── input_selector.py
│   └── run_pipeline.py
├── src/
│   ├── __init__.py
│   ├── api_client.py
│   ├── config_loader.py
│   ├── database.py
│   ├── ftp_client.py
│   ├── logging_utils.py
│   ├── pipeline.py
│   ├── scheduler.py
│   ├── schema_generator.py
│   └── transformers.py
├── tests/
│   ├── test_api_client.py
│   ├── test_config_loader.py
│   ├── test_database.py
│   └── test_logging_utils.py
│   └── test_pipeline.py
│   └── test_scheduler.py
│   └── test_schema_generator.py
├── .env
├── pipeline.log
├── pyproject.toml
├── requirements.txt
└── README.md

# How Each Part Works
- src/: All core pipeline logic and reusable modules.
Import modules here in scripts, e.g. from src.pipeline import DataPipeline.

- sample_api/: Local Flask API for testing data ingestion.
Run with python -m sample_api.app to simulate a REST API source.

- scripts/: Thin wrappers or entry points (like run_pipeline.py and input_selector.py).
These set up the environment, parse CLI arguments or handle GUI, and call into src/ for all real logic.

- config/: All configuration YAMLs (api_config.yaml, ftp_config.yaml).
No code—just configs describing sources, destinations, and pipeline behavior.

- data/: Output files only (e.g. output.csv, logs, pipeline-generated artifacts).
No code or configs.

- ftp_downloads/: Temporary or persistent storage for files downloaded via FTP/SFTP.
The pipeline reads from here after FTP download.

- tests/: Unit and integration tests for all modules in src/.
Run with pytest. No production code or configs here.

- .env: Stores environment variables (such as DB credentials, API tokens).
Loaded automatically by scripts at runtime.

- pyproject.toml / requirements.txt: Manage your dependencies and packaging.
Use pip install -r requirements.txt to install dependencies.

- pipeline.log: Main log file for pipeline runs. Useful for debugging and auditing.

- README.md: Project documentation and quickstart instructions.

# To Run Sample API
- Run your sample API
python -m sample_api.app

# Starting Postgres
- To enter the correct dir
cd C:\Postgres\postgresql-16.0-1-windows-x64-binaries\pgsql\bin

## 1st cmd prompt 
- To start
pg_ctl.exe start -D ../data
- To stop
pg_ctl.exe stop -D ../data

## 2nd cmd prompt (To connect)
C:\Postgres\postgresql-16.0-1-windows-x64-binaries\pgsql\bin\

## To run system through input selector
python -m scripts.input_selector

## To run system Explicitly
- ftp
python -m scripts.run_pipeline config/ftp_config.yaml
- api
python -m scripts.run_pipeline config/api_config.yaml
psql.exe -h localhost -p 5432 -U postgres -d DataLake
## To test files individually
pytest tests\test_file_name.py

## To test all files
pytest