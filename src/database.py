import os
import psycopg2
import csv
import logging
from dotenv import load_dotenv
from datetime import datetime

logger = logging.getLogger(__name__)
load_dotenv()

def get_connection():
    """Establish database connection using environment variables"""
    logger.debug("Establishing database connection to %s:%s/%s as user '%s'",
                 os.getenv("DB_HOST"), os.getenv("DB_PORT"), os.getenv("DB_NAME"), os.getenv("DB_USER"))
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )

def create_logins_table_if_not_exists(conn_params: dict = None):
    """
    Create the 'logins' table if it does not exist.
    Columns: Name, E-mail, Role, Username, Password, Last Login
    """
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS logins (
        id SERIAL PRIMARY KEY,
        name VARCHAR(50) NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        role VARCHAR(20) NOT NULL DEFAULT 'User',
        username VARCHAR(50) UNIQUE NOT NULL,
        password VARCHAR(100) NOT NULL,
        last_login TIMESTAMP
    );
    """
    try:
        if conn_params:
            conn = psycopg2.connect(**conn_params)
        else:
            conn = get_connection()
        cur = conn.cursor()
        cur.execute(create_table_sql)
        conn.commit()
        cur.close()
        conn.close()
        logger.info("Ensured 'logins' table exists.")
    except Exception as e:
        logger.error(f"Failed to create 'logins' table: {e}")
        if 'conn' in locals():
            conn.close()
        raise

def load_csv_to_db(csv_path: str, table_name: str, conn_params: dict):
    """
    Load CSV data into the database using plain INSERTs (no UPSERT, no primary key logic).
    """
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames:
                logger.error("CSV file has no columns")
                return
            columns = [col.strip() for col in reader.fieldnames]
            columns_str = ', '.join([f'"{col}"' for col in columns])
            placeholders = ', '.join(['%s'] * len(columns))
            insert_sql = f'INSERT INTO "{table_name}" ({columns_str}) VALUES ({placeholders})'

            rows = []
            for row in reader:
                rows.append(tuple(row[col] for col in reader.fieldnames))

        with psycopg2.connect(**conn_params) as conn:
            with conn.cursor() as cur:
                cur.executemany(insert_sql, rows)
                conn.commit()
                logger.info(f"INSERT completed: {len(rows)} rows from '{csv_path}' into table '{table_name}'")

    except Exception as e:
        logger.error(f"Failed to INSERT CSV '{csv_path}' into table '{table_name}': {e}")
        raise

def execute_query(query: str, params=None, conn_params: dict = None):
    try:
        if conn_params:
            conn = psycopg2.connect(**conn_params)
        else:
            conn = get_connection()
        cur = conn.cursor()
        if params:
            cur.execute(query, params)
        else:
            cur.execute(query)
        if query.strip().upper().startswith('SELECT'):
            results = cur.fetchall()
            conn.close()
            return results
        else:
            conn.commit()
            conn.close()
            logger.info("Query executed successfully")
    except Exception as e:
        logger.error(f"Failed to execute query: {e}")
        if 'conn' in locals():
            conn.close()
        raise

def table_exists(table_name: str, conn_params: dict = None) -> bool:
    try:
        query = """
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = %s
        );
        """
        result = execute_query(query, (table_name,), conn_params)
        return result[0][0] if result else False
    except Exception as e:
        logger.error(f"Failed to check if table exists: {e}")
        return False

def drop_table(table_name: str, conn_params: dict = None):
    try:
        query = f'DROP TABLE IF EXISTS "{table_name}" CASCADE;'
        execute_query(query, conn_params=conn_params)
        logger.info(f"Table '{table_name}' dropped successfully")
    except Exception as e:
        logger.error(f"Failed to drop table '{table_name}': {e}")
        raise

def get_table_row_count(table_name: str, conn_params: dict = None) -> int:
    try:
        query = f'SELECT COUNT(*) FROM "{table_name}";'
        result = execute_query(query, conn_params=conn_params)
        return result[0][0] if result else 0
    except Exception as e:
        logger.error(f"Failed to get row count for table '{table_name}': {e}")
        return 0
    
def log_pipeline_stats(stats: dict, conn_params: dict):
    """Atomic stats logging with self-healing schema"""
    from datetime import date
    
    if not conn_params:
        logger.error("No connection parameters provided for stats logging")
        return

    try:
        # Always verify table exists before logging
        from src.schema_generator import CSVSchemaGenerator
        CSVSchemaGenerator().create_pipeline_stats_table(conn_params)
        
        query = """
        INSERT INTO pipeline_stats 
            (stat_date, records_fetched, records_inserted, error_count, status)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (stat_date) DO UPDATE SET
            records_fetched = EXCLUDED.records_fetched,
            records_inserted = EXCLUDED.records_inserted,
            error_count = EXCLUDED.error_count,
            status = EXCLUDED.status;
        """
        execute_query(query, (
            date.today(),
            stats['records_fetched'],
            stats['records_inserted'],
            stats['error_count'],
            stats['status']
        ), conn_params)
        logger.info("Stats logged: %s", stats)
    except Exception as e:
        logger.error("Stats logging failed: %s", str(e))