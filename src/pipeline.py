import csv
import json
import os
import logging
from typing import List, Dict
from pathlib import Path
import pandas as pd

from src.api_client import APIClient
from src.config_loader import load_config, resolve_config_vars
from src.database import load_csv_to_db
from src.schema_generator import CSVSchemaGenerator
from src.ftp_client import download_ftp_files

logger = logging.getLogger(__name__)

class DataPipeline:
    def __init__(self, config_path: str):
        logger.info("Initializing DataPipeline with config: %s", config_path)
        self.config = resolve_config_vars(load_config(config_path))
        self.schema_generator = CSVSchemaGenerator()
        logger.debug("Pipeline configuration loaded: %s", self.config)
        logger.info("DataPipeline initialization complete")

    def fetch_data(self) -> List[Dict]:
        source_type = self.config['source']['type']
        if source_type == "REST_API":
            api_client = APIClient(self.config['source']['api'])
            return api_client.fetch_data()
        elif source_type == "FTP":
            ftp_config = resolve_config_vars(load_config("config/ftp_config.yaml"))
            ftp_cfg = ftp_config['ftp']
            # Uncomment the following lines to enable FTP download
            # download_ftp_files(
            #     host=ftp_cfg['host'],
            #     username=ftp_cfg['username'],
            #     password=ftp_cfg['password'],
            #     remote_dir=ftp_cfg['remote_dir'],
            #     local_dir=ftp_cfg['local_dir'],
            #     file_types=ftp_cfg.get('file_types', ['.csv', '.json', '.parquet'])
            # )
            return self._load_files_from_local(ftp_cfg['local_dir'])
        else:
            raise ValueError(f"Unknown source type: {source_type}")

    def _load_files_from_local(self, local_dir: str) -> List[Dict]:
        """Load and combine data from CSV, JSON, and Parquet files in a directory."""
        all_data = []
        for fname in os.listdir(local_dir):
            fpath = os.path.join(local_dir, fname)
            if fname.lower().endswith('.csv'):
                with open(fpath, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    all_data.extend(list(reader))
            elif fname.lower().endswith('.json'):
                with open(fpath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # If the JSON is a dict with a single key whose value is a list, use the list
                    if isinstance(data, dict) and len(data) == 1 and isinstance(next(iter(data.values())), list):
                        all_data.extend(next(iter(data.values())))
                    elif isinstance(data, list):
                        all_data.extend(data)
                    else:
                        all_data.append(data)
            elif fname.lower().endswith('.parquet'):
                df = pd.read_parquet(fpath)
                all_data.extend(df.to_dict(orient='records'))
        logger.info(f"Loaded {len(all_data)} records from FTP files in {local_dir}")
        return all_data

    def export_to_csv(self, data: List[Dict], output_path: str):
        """Export a list of dictionaries to a CSV file."""
        if not data:
            logger.warning("No data to export to CSV")
            return
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        logger.info("Exported %d records to CSV: %s", len(data), output_path)

    def run(self):
        logger.info("Starting DataPipeline execution")
        try:
            source_type = self.config['source']['type']
            raw_data = self.fetch_data()
            logger.info("Data fetch completed. Records retrieved: %d", len(raw_data))

            csv_output_path = self.config['destination']['csv']['output_path']
            logger.info("Exporting all data to CSV: %s", csv_output_path)
            self.export_to_csv(raw_data, csv_output_path)

            if self.config['destination']['database'].get('enabled'):
                logger.info("Database integration enabled, creating/updating table and loading data from CSV...")
                db_config = self.config['destination']['database']
                if source_type == "FTP":
                    table_name = db_config.get('table', 'ftp_data')
                elif source_type == "REST_API":
                    table_name = db_config.get('table', 'api_data')
                else:
                    table_name = db_config.get('table', 'data')
                conn_params = {
                    "host": os.getenv("DB_HOST"),
                    "port": os.getenv("DB_PORT"),
                    "dbname": os.getenv("DB_NAME"),
                    "user": os.getenv("DB_USER"),
                    "password": os.getenv("DB_PASSWORD"),
                }

                self.schema_generator.create_table_from_csv(csv_output_path, table_name, conn_params)
                load_csv_to_db(csv_output_path, table_name, conn_params)

                logger.info("Database insertion from CSV completed successfully")
            else:
                logger.warning("Database integration not enabled")

            logger.info("DataPipeline execution completed successfully")

        except Exception as e:
            logger.error("Pipeline execution failed: %s", str(e))
            logger.debug("Pipeline failure details", exc_info=True)
            raise