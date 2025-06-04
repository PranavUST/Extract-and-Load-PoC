import os
import psycopg2
import csv
import logging
from dotenv import load_dotenv

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

def load_csv_to_db_with_upsert(csv_path: str, table_name: str, conn_params: dict):
    """
    Load CSV data using UPSERT (INSERT ... ON CONFLICT DO UPDATE)
    This handles duplicates gracefully without errors
    """
    try:
        conn = psycopg2.connect(**conn_params)
        cur = conn.cursor()
        
        # Read CSV to get column names
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            columns = reader.fieldnames
            
            if not columns:
                logger.warning("No columns found in CSV file")
                return
            
            # Build UPSERT query
            columns_str = ', '.join([f'"{col}"' for col in columns])
            placeholders = ', '.join(['%s'] * len(columns))
            
            # Build UPDATE SET clause (exclude primary key 'id')
            update_columns = [col for col in columns if col != 'id']
            if update_columns:
                update_set = ', '.join([f'"{col}" = EXCLUDED."{col}"' for col in update_columns])
                upsert_sql = f'''
                    INSERT INTO "{table_name}" ({columns_str}) 
                    VALUES ({placeholders})
                    ON CONFLICT (id) DO UPDATE 
                    SET {update_set}
                '''
            else:
                # If only ID column, just ignore conflicts
                upsert_sql = f'''
                    INSERT INTO "{table_name}" ({columns_str}) 
                    VALUES ({placeholders})
                    ON CONFLICT (id) DO NOTHING
                '''
            
            # Execute UPSERT for each row
            rows_processed = 0
            
            # Reset file pointer to read data
            f.seek(0)
            reader = csv.DictReader(f)
            
            for row in reader:
                values = [row[col] for col in columns]
                cur.execute(upsert_sql, values)
                rows_processed += 1
        
        conn.commit()
        logger.info(f"UPSERT completed: {rows_processed} rows processed from '{csv_path}' into table '{table_name}'")
        
    except Exception as e:
        logger.error(f"Failed to UPSERT CSV '{csv_path}' into table '{table_name}': {e}")
        raise
    finally:
        if 'conn' in locals():
            conn.close()

def load_csv_to_db(csv_path: str, table_name: str, conn_params: dict):
    """
    Legacy function - redirects to UPSERT version to avoid duplicate key errors
    """
    return load_csv_to_db_with_upsert(csv_path, table_name, conn_params)

def execute_query(query: str, params=None, conn_params: dict = None):
    """
    Execute a SQL query with optional parameters
    """
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
        
        # If it's a SELECT query, fetch results
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
    """
    Check if a table exists in the database
    """
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
    """
    Drop a table if it exists
    """
    try:
        query = f'DROP TABLE IF EXISTS "{table_name}" CASCADE;'
        execute_query(query, conn_params=conn_params)
        logger.info(f"Table '{table_name}' dropped successfully")
        
    except Exception as e:
        logger.error(f"Failed to drop table '{table_name}': {e}")
        raise

def get_table_row_count(table_name: str, conn_params: dict = None) -> int:
    """
    Get the number of rows in a table
    """
    try:
        query = f'SELECT COUNT(*) FROM "{table_name}";'
        result = execute_query(query, conn_params=conn_params)
        return result[0][0] if result else 0
        
    except Exception as e:
        logger.error(f"Failed to get row count for table '{table_name}': {e}")
        return 0
