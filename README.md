REST_API_Implementation/
├── config/
│   └── api_config.yaml
├── data/
│   └── output.csv
├── sample_api/
│   ├── __init__.py
│   └── app.py
│   └── posts.json
├── scripts/
│   └── run_pipeline.py
├── src/
│   ├── __init__.py
│   ├── api_client.py
│   ├── config_loader.py
│   ├── database.py
│   ├── pipeline.py
│   ├── schema_generator.py
│   └── transformers.py
├── tests/
│   └── test_pipeline.py
│   └── test_db.py
├── .env
├── pipeline.log
├── pyproject.toml
├── requirements.txt
└── README.md

# Key Points:
- All reusable Python code goes in src/ (your main package).
- sample_api/ is a standalone package for your test API.
- scripts/ holds any CLI or entry-point scripts.
- data/ holds outputs or raw data.
- config/ holds configuration files.
- tests/ contains your test suite.
- Project metadata (pyproject.toml, requirements.txt, etc.) lives at the root.

# How Each Part Works
- src/: All core logic. When importing in scripts, use from src.pipeline import DataPipeline.
- sample_api/: Your local Flask API for testing ingestion. Run with python -m sample_api.app.
- scripts/: Contains only thin wrappers or entry points that set up environment and call into src/.
- config/: Keeps all configuration YAMLs separate from code.
- data/: Output files, never code
- tests/: Unit or integration tests, can be run with pytest or similar.
- pyproject.toml/requirements.txt: For dependency and packaging management.


# To Run
- Run your sample API
python -m sample_api.app

- Run your pipeline
python scripts/run_pipeline.py
--------------------------------


# Starting Postgres
- To enter the correct dir
cd C:\Postgres\postgresql-16.0-1-windows-x64-binaries\pgsql\bin

## 1st cmd prompt 
- To start
pg_ctl.exe start -D ../data
- To stop
pg_ctl.exe stop -D ../data

## 2nd cmd prompt (To connect)
C:\Postgres\postgresql-16.0-1-windows-x64-binaries\pgsql\bin\psql.exe -h localhost -p 5432 -U postgres -d DataLake
-----------------------------------------------------------------



