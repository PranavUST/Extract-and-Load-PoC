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
    
def log_pipeline_stats(stats: dict):
    """Log pipeline statistics to database (aggregated daily)"""
    from datetime import date
    query = """
    INSERT INTO pipeline_stats 
        (stat_date, records_fetched, records_inserted, error_count, total_runs, status)
    VALUES (%s, %s, %s, %s, 1, %s)
    ON CONFLICT (stat_date) DO UPDATE SET
        records_fetched = pipeline_stats.records_fetched + EXCLUDED.records_fetched,
        records_inserted = pipeline_stats.records_inserted + EXCLUDED.records_inserted,
        error_count = pipeline_stats.error_count + EXCLUDED.error_count,
        total_runs = pipeline_stats.total_runs + 1,
        status = EXCLUDED.status;
    """
    values = (
        date.today(),
        stats.get('records_fetched', 0),
        stats.get('records_inserted', 0),
        stats.get('error_count', 0),
        stats.get('status', 'unknown')
    )
    execute_query(query, values)
    # Log the update using the existing logger and logfile
    logger.info(
        f"pipeline_stats updated: Date={values[0]}, "
        f"Fetched={values[1]}, Inserted={values[2]}, "
        f"Errors={values[3]}, Runs incremented, Status={values[4]}"
    )