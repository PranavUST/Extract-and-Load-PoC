import ftplib
import os
import logging
import time
from typing import List
from src.database import insert_pipeline_status

logger = logging.getLogger(__name__)

def download_ftp_files(
    host: str,
    username: str,
    password: str,
    remote_dir: str,
    local_dir: str,
    file_types: List[str] = None,
    retries: int = 3,
    delay: int = 5,
    run_id: str = None
) -> List[str]:
    """
    Robust FTP downloader with improved error handling.
    Returns list of downloaded file paths (empty list if none).
    """
    downloaded_files = []
    attempt = 0
    
    logger.info("Starting FTP download to: %s", local_dir)
    logger.debug("Connection params - Host: %s, User: %s, Remote: %s", 
                host, username, remote_dir)

    while attempt < retries:
        try:
            # Create local directory if needed
            os.makedirs(local_dir, exist_ok=True)
            
            # Validate directory permissions
            if not os.access(local_dir, os.W_OK):
                raise PermissionError(f"Cannot write to {local_dir}")

            with ftplib.FTP(host, timeout=30) as ftp:
                ftp.login(user=username, passwd=password)
                ftp.cwd(remote_dir)
                
                files = ftp.nlst()
                logger.info("Found %d files in %s", len(files), remote_dir)
                
                for filename in files:
                    # Ensure file_types is a list of lowercase extensions with dot
                    if file_types:
                        logger.info("Filtering for file types: %s", file_types)
                        file_types_lc = [ft.lower() if ft.startswith('.') else f'.{ft.lower()}' for ft in file_types]
                        if not filename.lower().endswith(tuple(file_types_lc)):
                            logger.debug("Skipping non-matching file: %s", filename)
                            continue
                    logger.info("Files found on FTP: %s", files)     
                    local_path = os.path.join(local_dir, filename)
                    
                    # Skip existing files
                    if os.path.exists(local_path):
                        logger.debug("File exists, skipping: %s", filename)
                        continue
                    
                    logger.info("Downloading %s", filename)
                    with open(local_path, 'wb') as f:
                        ftp.retrbinary(f"RETR {filename}", f.write)
                    
                    downloaded_files.append(local_path)
                
                # Success: exit loop
                break

        except ftplib.error_perm as e:
            logger.error("FTP Error: %s", e)
            # Do NOT insert every FTP error, only final exhaustion below
            if "530" in str(e):
                logger.error("Invalid credentials")
            break  # Don't retry on permission errors
        except Exception as e:
            attempt += 1
            logger.error("Attempt %d/%d failed: %s", attempt, retries, e)
            insert_pipeline_status(f"Attempt {attempt}/{retries} failed: {e}", run_id=run_id, log_level="ERROR", module="ftp_client")
            if attempt < retries:
                time.sleep(delay)
            else:
                logger.error("All %d retries exhausted", retries)
                insert_pipeline_status(f"All {retries} retries exhausted", run_id=run_id, log_level="ERROR", module="ftp_client")
                break

    return downloaded_files
