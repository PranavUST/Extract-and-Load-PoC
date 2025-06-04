import csv
import logging
from typing import List, Dict
from pathlib import Path
import os
import json

<<<<<<< Updated upstream
from api_client import APIClient
from config_loader import load_config, resolve_config_vars
from database import load_csv_to_db
from schema_generator import CSVSchemaGenerator
=======
from src.api_client import APIClient
from src.config_loader import load_config, resolve_config_vars
from src.database import load_csv_to_db_with_upsert
from src.schema_generator import CSVSchemaGenerator
from src.ftp_client import download_ftp_files
>>>>>>> Stashed changes

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
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
        logger.info("Starting CSV export to: %s", output_path)
        if not data:
            logger.warning("No data to export to CSV")
            return
=======
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
        """Export data to CSV format."""
        if not data:
            logger.warning("No data to export")
            return

        logger.info("Starting CSV export to: %s", output_path)
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Get all unique fieldnames from all records
        all_fieldnames = set()
        for record in data:
            all_fieldnames.update(record.keys())
        all_fieldnames = sorted(list(all_fieldnames))
        
        # Write CSV
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=all_fieldnames)
            writer.writeheader()
            
            for record in data:
                # Clean the record before writing
                cleaned_record = {}
                for field in all_fieldnames:
                    value = record.get(field, '')
                    
                    # Clean different data types
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
            api_client = APIClient(self.config['source']['api'])
            return api_client.fetch_data()
        elif source_type == "FTP":
            from src.config_loader import load_config, resolve_config_vars
            ftp_config = resolve_config_vars(load_config("config/ftp_config.yaml"))
            ftp_cfg = ftp_config['ftp']
            download_ftp_files(
                host=ftp_cfg['host'],
                username=ftp_cfg['username'],
                password=ftp_cfg['password'],
                remote_dir=ftp_cfg['remote_dir'],
                local_dir=ftp_cfg['local_dir'],
                file_types=ftp_cfg.get('file_types', ['.csv', '.json', '.parquet'])
            )
            return self._load_files_from_local(ftp_cfg['local_dir'])
        else:
            raise ValueError(f"Unknown source type: {source_type}")
>>>>>>> Stashed changes

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        mode = 'w' if self.config['destination']['csv']['write_mode'] == 'overwrite' else 'a'
        logger.debug("CSV write mode: %s", mode)

<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
        all_fieldnames = list(data[0].keys())

        # Define field-specific cleaning rules
        field_rules = {
            'age': self._clean_integer,
            'salary': self._clean_float,
            'price': self._clean_float,
            'rating': self._clean_float,
            'view_count': self._clean_integer
        }

        # JSON fields should be handled separately
        json_fields = ['tags', 'metadata', 'address', 'skills', 'dimensions', 'items']

        try:
            with open(output_path, mode, newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=all_fieldnames,
                    restval='',
                    quoting=csv.QUOTE_MINIMAL
                )
                if mode == 'w':
                    writer.writeheader()
                    logger.debug("CSV header written")
                
                for record in data:
                    cleaned = {}
                    for field in all_fieldnames:
                        value = record.get(field)
                        
                        # Apply field-specific cleaning
                        if field in field_rules:
                            cleaned_value = field_rules[field](value)
                        elif field in json_fields:
                            cleaned_value = self._clean_json(value)
                        else:
                            cleaned_value = value
                        
                        cleaned[field] = cleaned_value
                    
                    writer.writerow(cleaned)
            
            logger.info("Successfully exported %d records to %s", len(data), output_path)
        except Exception as e:
            logger.error("Failed to export CSV to %s: %s", output_path, e)
            raise

    def _clean_integer(self, value):
        """Clean and validate integer fields"""
        try:
            return int(value) if value not in [None, ""] else None
        except (ValueError, TypeError):
            logger.warning("Invalid integer value: %s", value)
            return None

    def _clean_float(self, value):
        """Clean and validate float fields"""
        try:
            return float(value) if value not in [None, ""] else None
        except (ValueError, TypeError):
            logger.warning("Invalid float value: %s", value)
            return None

    def _clean_json(self, value):
        """Clean and validate JSON fields"""
        if isinstance(value, (dict, list)):
            return json.dumps(value)
        try:
            if value and json.loads(value):
                return value
        except (json.JSONDecodeError, TypeError):
            pass
        return 'null'

    def run(self):
        logger.info("Starting DataPipeline execution")
        try:
            # Fetch data from API
            logger.info("Fetching data from API")
            raw_data = self.api_client.fetch_data()
            logger.info("API data fetch completed. Records retrieved: %d", len(raw_data))

            # Export all records to a single CSV
=======
    # ADD THIS METHOD - This is what's missing!
    def run(self, csv_only=False):
        logger.info("Starting DataPipeline execution")
        try:
=======
    # ADD THIS METHOD - This is what's missing!
    def run(self, csv_only=False):
        logger.info("Starting DataPipeline execution")
        try:
>>>>>>> Stashed changes
=======
    # ADD THIS METHOD - This is what's missing!
    def run(self, csv_only=False):
        logger.info("Starting DataPipeline execution")
        try:
>>>>>>> Stashed changes
            # Fetch data
            logger.info("Fetching data")
            raw_data = self.fetch_data()
            logger.info("Data fetch completed. Records retrieved: %d", len(raw_data))

            # ALWAYS export to CSV
<<<<<<< Updated upstream
<<<<<<< Updated upstream
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
            csv_output_path = self.config['destination']['csv']['output_path']
            logger.info("Exporting all data to CSV: %s", csv_output_path)
            self.export_to_csv(raw_data, csv_output_path)

            # CONDITIONALLY run database operations
            if csv_only:
                logger.info("CSV-only mode: Skipping database operations")
            elif self.config['destination']['database']['enabled']:
                logger.info("Database integration enabled, running UPSERT operations...")
                db_config = self.config['destination']['database']
                table_name = db_config.get('table', 'api_data')

                conn_params = {
                    "host": os.getenv("DB_HOST"),
                    "port": os.getenv("DB_PORT"),
                    "dbname": os.getenv("DB_NAME"),
                    "user": os.getenv("DB_USER"),
                    "password": os.getenv("DB_PASSWORD"),
                }

<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
                # Step 1: Create or update table based on CSV schema
                logger.info("Creating or updating table '%s' based on CSV schema", table_name)
                self.schema_generator.create_table_from_csv(csv_output_path, table_name, conn_params)

                # Step 2: Load CSV data into the table
                logger.info("Loading CSV data into table '%s'", table_name)
                load_csv_to_db(csv_output_path, table_name, conn_params)
=======
                # Create table if needed
                logger.info("Creating or updating table '%s' based on CSV schema", table_name)
                self.schema_generator.create_table_from_csv(csv_output_path, table_name, conn_params)
>>>>>>> Stashed changes

=======
                # Create table if needed
                logger.info("Creating or updating table '%s' based on CSV schema", table_name)
                self.schema_generator.create_table_from_csv(csv_output_path, table_name, conn_params)

>>>>>>> Stashed changes
=======
                # Create table if needed
                logger.info("Creating or updating table '%s' based on CSV schema", table_name)
                self.schema_generator.create_table_from_csv(csv_output_path, table_name, conn_params)

>>>>>>> Stashed changes
                # Load data with UPSERT
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
