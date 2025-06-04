import os
import psycopg2
import csv
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv()

def get_connection():
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
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
    Loads CSV data with duplicate handling using ON CONFLICT DO NOTHING
=======
    Load CSV data using UPSERT (INSERT ... ON CONFLICT DO UPDATE)
    This handles duplicates gracefully without errors
>>>>>>> Stashed changes
=======
    Load CSV data using UPSERT (INSERT ... ON CONFLICT DO UPDATE)
    This handles duplicates gracefully without errors
>>>>>>> Stashed changes
=======
    Load CSV data using UPSERT (INSERT ... ON CONFLICT DO UPDATE)
    This handles duplicates gracefully without errors
>>>>>>> Stashed changes
    """
    try:
        conn = psycopg2.connect(**conn_params)
        cur = conn.cursor()
        
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
        # Read CSV and insert with conflict handling
=======
        # Read CSV to get column names
>>>>>>> Stashed changes
=======
        # Read CSV to get column names
>>>>>>> Stashed changes
=======
        # Read CSV to get column names
>>>>>>> Stashed changes
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            columns = reader.fieldnames
            
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
            # Create INSERT statement with ON CONFLICT
            placeholders = ', '.join(['%s'] * len(columns))
            columns_str = ', '.join([f'"{col}"' for col in columns])
            
            sql = f'''
                INSERT INTO "{table_name}" ({columns_str}) 
                VALUES ({placeholders})
                ON CONFLICT (id) DO NOTHING
            '''
            
            # Insert rows one by one (or use execute_values for batch)
            rows_inserted = 0
            for row in reader:
                values = [row[col] for col in columns]
                cur.execute(sql, values)
                if cur.rowcount > 0:
                    rows_inserted += 1
        
        conn.commit()
        logger.info(f"Loaded CSV '{csv_path}' into table '{table_name}'. {rows_inserted} new records inserted.")
=======
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
>>>>>>> Stashed changes
=======
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
>>>>>>> Stashed changes
=======
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
>>>>>>> Stashed changes
        
    except Exception as e:
        logger.error(f"Failed to UPSERT CSV '{csv_path}' into table '{table_name}': {e}")
        raise
    finally:
        if 'conn' in locals():
            conn.close()

# Keep the original function for backward compatibility
def load_csv_to_db(csv_path: str, table_name: str, conn_params: dict):
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
    try:
        conn = psycopg2.connect(**conn_params)
        with conn.cursor() as cur:
            with open(csv_path, 'r', encoding='utf-8') as f:
                # Use ON CONFLICT to ignore duplicates
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
        conn.close()

=======
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
    """
    Legacy function - redirects to UPSERT version to avoid duplicate key errors
    """
    return load_csv_to_db_with_upsert(csv_path, table_name, conn_params)
<<<<<<< Updated upstream
<<<<<<< Updated upstream
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
