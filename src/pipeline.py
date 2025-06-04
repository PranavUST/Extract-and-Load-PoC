import csv
import json
import os
import logging
from typing import List, Dict
from pathlib import Path

from src.api_client import APIClient
from src.config_loader import load_config, resolve_config_vars
from src.database import load_csv_to_db_with_upsert
from src.schema_generator import CSVSchemaGenerator
from src.ftp_client import download_ftp_files

logger = logging.getLogger(__name__)

class DataPipeline:
    def __init__(self, config_path: str):
        logger.info("Initializing DataPipeline with config: %s", config_path)
        self.config = resolve_config_vars(load_config(config_path))
        self.api_client = APIClient(self.config['source']['api'])
        self.schema_generator = CSVSchemaGenerator()
        logger.debug("Pipeline configuration loaded: %s", self.config)
        logger.info("DataPipeline initialization complete")

    def export_to_csv(self, data: List[Dict], output_path: str):
        """Export data to CSV format."""
        if not data:
            logger.warning("No data to export")
            return

        logger.info("Starting CSV export to: %s", output_path)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Collect all unique fieldnames
        all_fieldnames = set()
        for record in data:
            all_fieldnames.update(record.keys())
        all_fieldnames = sorted(list(all_fieldnames))

        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=all_fieldnames)
            writer.writeheader()
            for record in data:
                cleaned_record = {}
                for field in all_fieldnames:
                    value = record.get(field, '')
                    if isinstance(value, (int, float)):
                        cleaned_record[field] = value
                    elif isinstance(value, (list, dict)):
                        cleaned_record[field] = json.dumps(value)
                    elif isinstance(value, str):
                        cleaned_record[field] = value.strip()
                    else:
                        cleaned_record[field] = str(value) if value is not None else ''
                writer.writerow(cleaned_record)
        logger.info("Successfully exported %d records to %s", len(data), output_path)

    def fetch_data(self) -> List[Dict]:
        source_type = self.config['source']['type']
        if source_type == "FTP":
            ftp_cfg = self.config['source']['ftp']
            downloaded_files = download_ftp_files(
                host=ftp_cfg['host'],
                username=ftp_cfg['username'],
                password=ftp_cfg['password'],
                remote_dir=ftp_cfg['remote_dir'],
                local_dir=ftp_cfg['local_dir'],
                file_types=ftp_cfg.get('file_types', ['.csv', '.json', '.parquet']),
                retries=ftp_cfg.get('retries', 3),
            )
            if not downloaded_files:
                logger.warning("No files downloaded from FTP server. Returning empty list.")
                return []
            data = self._load_files_from_local(ftp_cfg['local_dir'])
            return data if data else []
        elif source_type == "REST_API":
            data = self.api_client.fetch_data()
            return data if data else []
        else:
            logger.error(f"Unknown source type: {source_type}. Returning empty list.")
            return []

    def _load_files_from_local(self, local_dir: str) -> List[Dict]:
        all_data = []
        try:
            if not os.path.exists(local_dir):
                logger.error(f"Local directory does not exist: {local_dir}")
                return []
            
            for fname in os.listdir(local_dir):
                fpath = os.path.join(local_dir, fname)
                if fname.lower().endswith('.csv'):
                    with open(fpath, 'r', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        all_data.extend(list(reader))
                elif fname.lower().endswith('.json'):
                    with open(fpath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if isinstance(data, list):
                            all_data.extend(data)
                        else:
                            all_data.append(data)
                elif fname.lower().endswith('.parquet'):
                    import pandas as pd
                    df = pd.read_parquet(fpath)
                    all_data.extend(df.to_dict(orient='records'))
        except Exception as e:
            logger.error(f"Error loading files from {local_dir}: {e}")
        return all_data  # Returns empty list on failure

    def run(self, csv_only=False):
        logger.info("Starting DataPipeline execution")
        try:
            logger.info("Fetching data")
            raw_data = self.fetch_data() or []  # Ensure it's never None
            logger.info("Data fetch completed. Records retrieved: %d", len(raw_data))

            # Always export to CSV
            csv_output_path = self.config['destination']['csv']['output_path']
            logger.info("Exporting all data to CSV: %s", csv_output_path)
            self.export_to_csv(raw_data, csv_output_path)

            # Conditionally run database operations
            if csv_only:
                logger.info("CSV-only mode: Skipping database operations")
            elif self.config['destination']['database'].get('enabled'):
                logger.info("Database integration enabled, running UPSERT operations...")
                db_config = self.config['destination']['database']
                table_name = db_config.get('table', 'api_data' if self.config['source']['type'] == "REST_API" else 'ftp_data')
                conn_params = {
                    "host": os.getenv("DB_HOST"),
                    "port": os.getenv("DB_PORT"),
                    "dbname": os.getenv("DB_NAME"),
                    "user": os.getenv("DB_USER"),
                    "password": os.getenv("DB_PASSWORD"),
                }
                logger.info("Creating or updating table '%s' based on CSV schema", table_name)
                self.schema_generator.create_table_from_csv(csv_output_path, table_name, conn_params)
                logger.info("Loading CSV data into table '%s' using UPSERT", table_name)
                load_csv_to_db_with_upsert(csv_output_path, table_name, conn_params)
                logger.info("UPSERT operations completed successfully")
            else:
                logger.warning("Database integration not enabled")

            logger.info("DataPipeline execution completed successfully")

        except Exception as e:
            logger.error("Pipeline execution failed: %s", str(e))
            logger.debug("Pipeline failure details", exc_info=True)
            raise
