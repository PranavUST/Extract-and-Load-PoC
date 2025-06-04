import ftplib
import os
import logging
import time
from typing import List

logger = logging.getLogger(__name__)

def download_ftp_files(
    host: str,
    username: str,
    password: str,
    remote_dir: str,
    local_dir: str,
    file_types: List[str] = None,
    retries: int = 3,
    delay: int = 5
) -> List[str]:
    """
    Robust FTP downloader with improved error handling
    Returns list of downloaded file paths (empty list if none)
    """
    downloaded_files = []
    attempt = 0
    
    logger.info("Starting FTP download to: %s", local_dir)
    logger.debug("Connection params - Host: %s, User: %s, Remote: %s", 
                host, username, remote_dir)

    while attempt <= retries:
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
                    if file_types and not filename.lower().endswith(tuple(file_types)):
                        logger.debug("Skipping non-matching file: %s", filename)
                        continue
                        
                    local_path = os.path.join(local_dir, filename)
                    
                    # Skip existing files
                    if os.path.exists(local_path):
                        logger.debug("File exists, skipping: %s", filename)
                        continue
                        
                    logger.info("Downloading %s", filename)
                    with open(local_path, 'wb') as f:
                        ftp.retrbinary(f"RETR {filename}", f.write)
                    
                    downloaded_files.append(local_path)
                
                return downloaded_files

        except ftplib.error_perm as e:
            logger.error("FTP Error: %s", e)
            if "530" in str(e):
                logger.error("Invalid credentials")
            return []
        except Exception as e:
            attempt += 1
            logger.error("Attempt %d/%d failed: %s", attempt, retries, e)
            if attempt <= retries:
                time.sleep(delay)
    
    logger.error("All %d retries exhausted", retries)
    return []
