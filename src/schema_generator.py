import csv
import logging
from typing import Dict, Optional
import psycopg2
import re
import json

logger = logging.getLogger(__name__)

class CSVSchemaGenerator:
    """Generates PostgreSQL table schemas from CSV files"""

    def __init__(self):
        self.type_mapping = {
            'INTEGER': 'INTEGER',
            'REAL': 'REAL',
            'BOOLEAN': 'BOOLEAN',
            'TIMESTAMP': 'TIMESTAMP',
            'DATE': 'DATE',
            'JSONB': 'JSONB',
            'TEXT': 'TEXT'
        }

    def infer_column_type(self, values):
        """
        Infer PostgreSQL data type from a list of sample values.
        """
        non_empty = [v for v in values if v and v.strip()]
        if not non_empty:
            return "TEXT"

        if any(self._looks_like_timestamp(v) for v in non_empty):
            return "TIMESTAMP"
        if any(self._looks_like_date(v) for v in non_empty):
            return "DATE"
        if all(self._is_integer(v) for v in non_empty):
            return "INTEGER"
        if all(self._is_float(v) for v in non_empty):
            return "REAL"
        if all(self._is_boolean(v) for v in non_empty):
            return "BOOLEAN"
        if any(self._looks_like_json(v) for v in non_empty):
            return "JSONB"
        return "TEXT"

    def _is_integer(self, value):
        try:
            int(value)
            return True
        except ValueError:
            return False

    def _is_float(self, value):
        try:
            float(value)
            return True
        except ValueError:
            return False

    def _is_boolean(self, value):
        return str(value).lower() in {'true', 'false', 't', 'f', '1', '0', 'yes', 'no'}

    def _looks_like_timestamp(self, value: str) -> bool:
        """Check if a string value looks like a timestamp"""
        timestamp_patterns = [
            r'^\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}(\.\d+)?([Zz+-]\d{2}:?\d{2})?$',
            r'^\d{4}-\d{2}-\d{2}$'
        ]
        return any(re.match(p, value.strip()) for p in timestamp_patterns)

    def _looks_like_date(self, value: str) -> bool:
        """Check if a string value looks like a date"""
        date_patterns = [
            r'^\d{4}-\d{2}-\d{2}$',
            r'^\d{2}/\d{2}/\d{4}$',
            r'^\d{2}-\d{2}-\d{4}$'
        ]
        return any(re.match(p, value.strip()) for p in date_patterns)

    def _looks_like_json(self, value: str) -> bool:
        """Check if a string value is valid JSON"""
        value = value.strip()
        if not value:
            return False
        try:
            json.loads(value)
            return True
        except json.JSONDecodeError:
            return False

    def analyze_csv_schema(self, csv_path: str, sample_size: int = 100) -> Dict[str, str]:
        """
        Analyze a CSV file to determine column names and PostgreSQL types.
        """
        logger.info("Analyzing CSV schema from: %s", csv_path)
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                fieldnames = reader.fieldnames
                if not fieldnames:
                    raise ValueError("CSV file has no header row")
                samples = {field: [] for field in fieldnames}
                row_count = 0
                for row in reader:
                    for field in fieldnames:
                        samples[field].append(row.get(field, ''))
                    row_count += 1
                    if row_count >= sample_size:
                        break
                schema = {}
                for field in fieldnames:
                    inferred_type = self.infer_column_type(samples[field])
                    schema[field] = inferred_type
                    logger.debug("Column '%s' detected as type: %s", field, inferred_type)
                logger.info("Schema analysis complete. Found %d columns", len(schema))
                return schema
        except Exception as e:
            logger.error("Failed to analyze CSV schema: %s", e)
            raise

    def generate_create_table_sql(self, table_name: str, column_types: Dict[str, str]) -> str:
        """
        Generate a CREATE TABLE SQL statement for the given table and column types.
        """
        columns = []
        primary_key = None
        if 'id' in column_types:
            primary_key = 'id'
            logger.info("Using 'id' as primary key")
        else:
            for col_name in column_types.keys():
                if col_name.endswith('_id'):
                    primary_key = col_name
                    logger.info("Auto-detected primary key: '%s'", primary_key)
                    break
        for column_name, column_type in column_types.items():
            if column_name == primary_key:
                columns.append(f'"{column_name}" {column_type} PRIMARY KEY')
            else:
                columns.append(f'"{column_name}" {column_type}')
        sql = f'CREATE TABLE IF NOT EXISTS "{table_name}" (\n'
        sql += ',\n'.join(f'    {col}' for col in columns)
        sql += '\n);'
        return sql

    def create_table_from_csv(self, csv_path: str, table_name: str, conn_params: Dict) -> None:
        """
        Create a PostgreSQL table based on CSV structure and data types.
        """
        logger.info("Creating table '%s' from CSV: %s", table_name, csv_path)
        schema = self.analyze_csv_schema(csv_path)
        create_sql = self.generate_create_table_sql(table_name, schema)
        try:
            conn = psycopg2.connect(**conn_params)
            with conn.cursor() as cur:
                cur.execute(create_sql)
            conn.commit()
            logger.info("Successfully created table '%s'", table_name)
        except Exception as e:
            logger.error("Failed to create table '%s': %s", table_name, e)
            raise
        finally:
            if 'conn' in locals():
                conn.close()

    def execute_query(self, query: str, conn_params: dict):
            """Execute a raw SQL query using database.py's execute_query"""
            from src.database import execute_query  # Import here to avoid circular dependencies
            return execute_query(query, conn_params=conn_params)
    
    def create_pipeline_stats_table(self, conn_params: dict):
        """Idempotent table creation with explicit columns"""
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS pipeline_stats (
            stat_date DATE PRIMARY KEY,
            records_fetched INT NOT NULL,
            records_inserted INT NOT NULL,
            error_count INT DEFAULT 0,
            status VARCHAR(50) NOT NULL
        );
        """
        try:
            self.execute_query(create_table_sql, conn_params=conn_params)
            logger.info("Created/verified pipeline_stats table structure")
        except Exception as e:
            logger.critical("FAILED TO CREATE STATS TABLE: %s", str(e))
            raise

