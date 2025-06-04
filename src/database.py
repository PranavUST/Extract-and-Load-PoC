import os
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv
import logging
import csv

logger = logging.getLogger(__name__)
load_dotenv()

def get_connection():
    """Establish and return a new database connection using environment variables."""
    logger.debug(
        "Establishing database connection to %s:%s/%s as user '%s'",
        os.getenv("DB_HOST"), os.getenv("DB_PORT"), os.getenv("DB_NAME"), os.getenv("DB_USER")
    )
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )

def load_csv_to_db_with_conflict_handling(csv_path, table_name, conn_params):
    """
    Loads CSV data with duplicate handling using ON CONFLICT DO NOTHING.
    """
    conn = None
    try:
        conn = psycopg2.connect(**conn_params)
        cur = conn.cursor()
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            columns = reader.fieldnames
            placeholders = ', '.join(['%s'] * len(columns))
            columns_str = ', '.join([f'"{col}"' for col in columns])
            sql = f'''
                INSERT INTO "{table_name}" ({columns_str}) 
                VALUES ({placeholders})
                ON CONFLICT (id) DO NOTHING
            '''
            rows_inserted = 0
            for row in reader:
                values = [row[col] for col in columns]
                cur.execute(sql, values)
                if cur.rowcount > 0:
                    rows_inserted += 1
        conn.commit()
        logger.info(f"Loaded CSV '{csv_path}' into table '{table_name}'. {rows_inserted} new records inserted.")
    except Exception as e:
        logger.error(f"Failed to load CSV '{csv_path}' into table '{table_name}': {e}")
        raise
    finally:
        if conn:
            conn.close()

def load_csv_to_db(csv_path: str, table_name: str, conn_params: dict):
    """
    Loads CSV data into a PostgreSQL table using COPY, ignoring duplicates.
    """
    conn = None
    try:
        conn = psycopg2.connect(**conn_params)
        with conn.cursor() as cur:
            with open(csv_path, 'r', encoding='utf-8') as f:
                sql = f'''
                COPY {table_name} FROM STDIN WITH CSV HEADER
                '''
                cur.copy_expert(sql, f)
            conn.commit()
        logger.info(f"Loaded CSV '{csv_path}' into table '{table_name}'")
    except Exception as e:
        logger.error(f"Failed to load CSV: {e}")
        raise
    finally:
        if conn:
            conn.close()