import csv
import json
import os
import logging
import pandas as pd
from typing import List, Dict
from datetime import datetime
from pathlib import Path
output_path = Path(__file__).parent.parent / 'data' / 'output.csv'
from src.api_client import APIClient
from src.config_loader import load_config, resolve_config_vars
from src.database import load_csv_to_db, log_pipeline_stats
from src.schema_generator import CSVSchemaGenerator
from src.ftp_client import download_ftp_files
from src.database import insert_pipeline_status

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)
def get_project_root():
    return Path(__file__).parent.parent
def resolve_path(path_from_config):
    p = Path(path_from_config)
    if not p.is_absolute():
        return get_project_root() / p
    return p
class DataPipeline:
    def __init__(self, config_path: str):
        logger.info("Initializing DataPipeline with config: %s", config_path)
        self.config = resolve_config_vars(load_config(config_path))
        source_type = self.config['source']['type']
        
        # Initialize source-specific components
        if source_type == "REST_API":
            self.api_client = APIClient(self.config['source']['api'])
        elif source_type == "FTP":
            self.ftp_config = self.config['source']['ftp']
        else:
            raise ValueError(f"Unsupported source type: {source_type}")
        
        # Common components
        self.schema_generator = CSVSchemaGenerator()
        logger.debug("Pipeline configuration loaded: %s", self.config)
        logger.info("DataPipeline initialization complete")
        logger.info(f"Current working directory: {os.getcwd()}")
        logger.info(f"Resolved output CSV path: {os.path.abspath(output_path)}")
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
        if source_type == "REST_API":
            return self.api_client.fetch_data()
        elif source_type == "FTP":
            # For local testing without FTP server
            if self.ftp_config.get('skip_download', False):
                logger.info("Skipping FTP download (local test mode)")
            else:
                downloaded_files = download_ftp_files(
                    host=self.ftp_config['host'],
                    username=self.ftp_config['username'],
                    password=self.ftp_config['password'],
                    remote_dir=self.ftp_config['remote_dir'],
                    local_dir=self.ftp_config['local_dir'],
                    file_types=self.ftp_config.get('file_types', ['.csv', '.json', '.parquet']),
                    retries=self.ftp_config.get('retries', 3),  # <-- add this line
                    delay=self.ftp_config.get('retry_delay', 5)
                )
                if not downloaded_files:
                    logger.error("FTP download failed. Will attempt to load files from local directory anyway.")
            # Always try to load from local directory, even if FTP failed
            return self._load_files_from_local(self.ftp_config['local_dir'])
        else:
            raise ValueError(f"Unknown source type: {source_type}")

    def _load_files_from_local(self, local_dir: str) -> List[Dict]:
        # Always resolve local_dir relative to project root
        local_dir = str((Path(__file__).parent.parent / local_dir).resolve())
        all_data = []
        if not os.path.exists(local_dir):
            logger.error("Local directory does not exist: %s", local_dir)
            return []

        logger.info("Loading files from local directory: %s", local_dir)
        logger.info("Files found: %s", os.listdir(local_dir))
        for fname in os.listdir(local_dir):
            fpath = os.path.join(local_dir, fname)
            try:
                if fname.lower().endswith('.json'):
                    with open(fpath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if isinstance(data, dict):
                            for key in data:
                                if isinstance(data[key], list):
                                    all_data.extend(data[key])
                        elif isinstance(data, list):
                            all_data.extend(data)
                elif fname.lower().endswith('.csv'):
                    with open(fpath, 'r', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        all_data.extend(list(reader))
                elif fname.lower().endswith('.parquet'):
                    df = pd.read_parquet(fpath)
                    all_data.extend(df.to_dict(orient='records'))
            except Exception as e:
                logger.error("Failed to load %s: %s", fname, str(e))
        logger.info("Total records loaded from local: %d", len(all_data))
        return all_data

    def run(self, run_id=None, csv_only=False):
        logger.info("Starting DataPipeline execution")
        insert_pipeline_status("Pipeline started.", run_id)
        stats = {
            'records_fetched': 0,  # Will be incremented during pipeline run
            'records_inserted': 0,  # Will be incremented during pipeline run
            'error_count': 0,      # Will be incremented on errors
            'status': 'success'    # Will be updated based on final state
        }

        # Initialize conn_params BEFORE try block
        conn_params = None
        if self.config['destination']['database'].get('enabled'):
            conn_params = {
                "host": os.getenv("DB_HOST"),
                "port": os.getenv("DB_PORT"),
                "dbname": os.getenv("DB_NAME"),
                "user": os.getenv("DB_USER"),
                "password": os.getenv("DB_PASSWORD"),
            }
            # Create stats table immediately
            try:
                self.schema_generator.create_pipeline_stats_table(conn_params)
                logger.info("Stats table initialized successfully")
            except Exception as e:
                logger.critical("Failed to create stats table: %s", str(e))

        try:
            logger.info("Fetching data")
            insert_pipeline_status("Fetching data...", run_id)
            raw_data = self.fetch_data() or []
            stats['records_fetched'] = len(raw_data)
            logger.info("Data fetch completed. Records retrieved: %d", stats['records_fetched'])
            insert_pipeline_status(f"Data fetch completed. Records retrieved: {stats['records_fetched']}", run_id)

            # Always export to CSV
            csv_output_path = self.config['destination']['csv']['output_path']
            csv_output_path = str((Path(__file__).parent.parent / csv_output_path).resolve())
            logger.info("Exporting all data to CSV: %s", csv_output_path)
            insert_pipeline_status(f"Exporting all data to CSV: {csv_output_path}", run_id)
            self.export_to_csv(raw_data, csv_output_path)
            stats['records_inserted'] = len(raw_data)
            insert_pipeline_status(f"Exported {len(raw_data)} records to CSV.", run_id)

            # Conditionally run database operations
            if csv_only:
                logger.info("CSV-only mode: Skipping database operations")
                insert_pipeline_status("CSV-only mode: Skipping database operations", run_id)
            elif self.config['destination']['database'].get('enabled'):
                logger.info("Database integration enabled, running INSERT operations...")
                insert_pipeline_status("Database integration enabled, running INSERT operations...", run_id)
                db_config = self.config['destination']['database']
                table_name = db_config.get('table', 'data')

                # Create main data table
                logger.info("Creating/updating table '%s'", table_name)
                insert_pipeline_status(f"Creating/updating table '{table_name}'", run_id)
                self.schema_generator.create_table_from_csv(csv_output_path, table_name, conn_params)
                
                # Load data
                logger.info("Loading CSV data into table '%s'", table_name)
                insert_pipeline_status(f"Loading CSV data into table '{table_name}'", run_id)
                load_csv_to_db(csv_output_path, table_name, conn_params)

            logger.info("DataPipeline execution completed successfully")
            insert_pipeline_status("Pipeline completed successfully.", run_id)

        except Exception as e:
            stats['error_count'] = 1
            stats['status'] = 'failed'
            logger.error("Pipeline execution failed: %s", str(e))
            insert_pipeline_status(f"Pipeline execution failed: {str(e)}", run_id)
            raise
        finally:
            # Stats logging with guaranteed conn_params availability
            try:
                if conn_params:
                    # Ensure stats table exists before logging
                    self.schema_generator.create_pipeline_stats_table(conn_params)
                    log_pipeline_stats(stats, conn_params)
                    logger.debug("Pipeline statistics logged: %s", stats)
                else:
                    logger.warning("Database not enabled - skipping stats logging")
            except Exception as e:
                logger.critical("FATAL: Stats logging failed: %s", str(e))
