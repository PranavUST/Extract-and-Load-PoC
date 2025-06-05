import csv
import json
import os
import logging
from typing import List, Dict
from datetime import datetime

from src.api_client import APIClient
from src.config_loader import load_config, resolve_config_vars
from src.database import load_csv_to_db, log_pipeline_stats
from src.schema_generator import CSVSchemaGenerator
from src.ftp_client import download_ftp_files

logger = logging.getLogger(__name__)

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
                    file_types=self.ftp_config.get('file_types', ['.csv', '.json', '.parquet'])
                )
                if not downloaded_files:
                    logger.error("FTP download failed. No new files processed.")
                    return []
            return self._load_files_from_local(self.ftp_config['local_dir'])
        else:
            raise ValueError(f"Unknown source type: {source_type}")

    def _load_files_from_local(self, local_dir: str) -> List[Dict]:
        all_data = []
        if not os.path.exists(local_dir):
            logger.error("Local directory does not exist: %s", local_dir)
            return []
            
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
                # Add CSV/Parquet handling here if needed
            except Exception as e:
                logger.error("Failed to load %s: %s", fname, str(e))
        return all_data

    def run(self, csv_only=False):
        logger.info("Starting DataPipeline execution")
        stats = {
            'records_fetched': 0,
            'records_inserted': 0,
            'error_count': 0,
            'status': 'success'
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
            raw_data = self.fetch_data() or []
            stats['records_fetched'] = len(raw_data)
            logger.info("Data fetch completed. Records retrieved: %d", stats['records_fetched'])

            # Always export to CSV
            csv_output_path = self.config['destination']['csv']['output_path']
            logger.info("Exporting all data to CSV: %s", csv_output_path)
            self.export_to_csv(raw_data, csv_output_path)
            stats['records_inserted'] = len(raw_data)

            # Conditionally run database operations
            if csv_only:
                logger.info("CSV-only mode: Skipping database operations")
            elif self.config['destination']['database'].get('enabled'):
                logger.info("Database integration enabled, running INSERT operations...")
                db_config = self.config['destination']['database']
                table_name = db_config.get('table', 'data')

                # Create main data table
                logger.info("Creating/updating table '%s'", table_name)
                self.schema_generator.create_table_from_csv(csv_output_path, table_name, conn_params)
                
                # Load data
                logger.info("Loading CSV data into table '%s'", table_name)
                load_csv_to_db(csv_output_path, table_name, conn_params)

            logger.info("DataPipeline execution completed successfully")

        except Exception as e:
            stats['error_count'] = 1
            stats['status'] = 'failed'
            logger.error("Pipeline execution failed: %s", str(e))
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
