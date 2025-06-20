import os
import psycopg2
import csv
import logging
from dotenv import load_dotenv
from datetime import datetime

logger = logging.getLogger(__name__)
load_dotenv()

def get_connection(conn_params=None):
    """Get database connection with provided params or default config"""
    try:
        if conn_params is None:
            # Load from environment variables (from .env or system env)
            conn_params = {
                'host': os.getenv('DB_HOST', 'localhost'),
                'database': os.getenv('DB_NAME', 'postgres'),
                'user': os.getenv('DB_USER', 'postgres'),
                'password': os.getenv('DB_PASSWORD', 'admin'),
                'port': os.getenv('DB_PORT', 5432)
            }
        return psycopg2.connect(**conn_params)
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        raise

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
    """Log pipeline stats with accumulation across all inserts"""
    from datetime import date
    import logging
    
    logger = logging.getLogger(__name__)

    try:
        with get_connection(conn_params) as conn:
            with conn.cursor() as cur:
                # Get today's current totals
                cur.execute("""
                    SELECT total_records_fetched, total_records_inserted, total_error_count 
                    FROM pipeline_stats 
                    WHERE stat_date = CURRENT_DATE;
                """)
                current_stats = cur.fetchone()

                # Each successful operation counts as new records, even if data is the same
                records_fetched = int(stats.get('records_fetched', 0))
                records_inserted = int(stats.get('records_inserted', 0))
                error_count = int(stats.get('error_count', 0))

                logger.debug(f"New records: fetched={records_fetched}, inserted={records_inserted}")

                if current_stats:
                    # Always add new operations to totals
                    total_fetched = current_stats[0] + records_fetched
                    total_inserted = current_stats[1] + records_inserted
                    total_errors = current_stats[2] + error_count

                    logger.debug(f"Updating totals: fetched={total_fetched}, inserted={total_inserted}")

                    cur.execute("""
                        UPDATE pipeline_stats 
                        SET total_records_fetched = %s,
                            total_records_inserted = %s,
                            total_error_count = %s,
                            last_status = %s,
                            last_run_timestamp = CURRENT_TIMESTAMP
                        WHERE stat_date = CURRENT_DATE
                    """, (total_fetched, total_inserted, total_errors, stats['status']))
                else:
                    # First run of the day
                    logger.debug("First run of the day")
                    cur.execute("""
                        INSERT INTO pipeline_stats 
                            (stat_date, total_records_fetched, total_records_inserted, 
                             total_error_count, last_status)
                        VALUES 
                            (CURRENT_DATE, %s, %s, %s, %s)
                    """, (records_fetched, records_inserted, error_count, stats['status']))

                conn.commit()

                logger.info(f"Pipeline stats updated - Total records fetched: {total_fetched if current_stats else records_fetched}, "
                          f"Total records inserted: {total_inserted if current_stats else records_inserted}")

    except Exception as e:
        logger.error(f"Failed to log pipeline stats: {str(e)}")
        raise
def create_pipeline_status_table_if_not_exists(conn_params: dict = None):
    """Create the pipeline_status table if it does not exist, with run_id, log_level, and module columns."""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS pipeline_status (
        id SERIAL PRIMARY KEY,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        message TEXT,
        run_id VARCHAR(64),
        log_level VARCHAR(16) DEFAULT 'INFO',
        module VARCHAR(64) DEFAULT NULL
    );
    """
    # Add columns if they do not exist (for migration)
    alter_sqls = [
        "ALTER TABLE pipeline_status ADD COLUMN IF NOT EXISTS log_level VARCHAR(16) DEFAULT 'INFO';",
        "ALTER TABLE pipeline_status ADD COLUMN IF NOT EXISTS module VARCHAR(64) DEFAULT NULL;"
    ]
    try:
        if conn_params:
            conn = psycopg2.connect(**conn_params)
        else:
            conn = get_connection()
        cur = conn.cursor()
        cur.execute(create_table_sql)
        for alter in alter_sqls:
            cur.execute(alter)
        conn.commit()
        cur.close()
        conn.close()
        logger.info("Ensured 'pipeline_status' table exists with log_level and module columns.")
    except Exception as e:
        logger.error(f"Failed to create/alter 'pipeline_status' table: {e}")
        if 'conn' in locals():
            conn.close()
        raise

def insert_pipeline_status(message: str, run_id: str = None, log_level: str = 'INFO', module: str = None, conn_params: dict = None):
    """Insert a pipeline status message into the database with log level and module."""
    logger.debug(f"insert_pipeline_status called with message='{message[:60]}...', run_id={run_id}, log_level={log_level}, module={module}, conn_params keys={list(conn_params.keys()) if conn_params else None}")
    try:
        if conn_params:
            logger.debug(f"Connecting to DB with conn_params: {conn_params}")
            conn = psycopg2.connect(**conn_params)
        else:
            logger.debug("Connecting to DB with default connection")
            conn = get_connection()
        cur = conn.cursor()
        if run_id:
            logger.debug(f"Inserting with run_id: {run_id}")
            cur.execute("INSERT INTO pipeline_status (message, run_id, log_level, module) VALUES (%s, %s, %s, %s)", (message, run_id, log_level, module))
        else:
            logger.debug("Inserting without run_id")
            cur.execute("INSERT INTO pipeline_status (message, log_level, module) VALUES (%s, %s, %s)", (message, log_level, module))
        conn.commit()
        cur.close()
        conn.close()
        logger.info(f"Inserted pipeline status: {message}")
    except Exception as e:
        logger.error(f"Failed to insert pipeline status: {e}")
        if 'conn' in locals():
            conn.close()
        raise