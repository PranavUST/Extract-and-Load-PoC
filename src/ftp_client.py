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
    Download files from an FTP server to a local directory with enhanced logging and retry logic.
    Returns list of downloaded file paths (empty list if none).
    """
    downloaded_files = []
    attempt = 0

    logger.info("Starting FTP download process")
    logger.debug(f"Connection parameters - Host: {host}, User: {username}, Remote Dir: {remote_dir}")

    while attempt < retries:
        try:
            # Ensure local directory exists
            logger.debug(f"Creating local directory: {local_dir}")
            os.makedirs(local_dir, exist_ok=True)

            # Validate local directory permissions
            if not os.access(local_dir, os.W_OK):
                raise PermissionError(f"No write permissions for local directory: {local_dir}")

            with ftplib.FTP(host, timeout=30) as ftp:
                logger.info(f"Connected to FTP server: {host}")

                # Login
                ftp.login(user=username, passwd=password)
                logger.debug("Authentication successful")

                # Change to remote directory
                ftp.cwd(remote_dir)
                logger.info(f"Changed to remote directory: {remote_dir}")

                # List files
                files = ftp.nlst()
                logger.info(f"Found {len(files)} files in remote directory: {files}")

                if not files:
                    logger.warning("No files found in remote directory")
                    return []

                # Filter and download files
                for filename in files:
                    if file_types and not any(filename.lower().endswith(ext.lower()) for ext in file_types):
                        logger.debug(f"Skipping non-matching file: {filename}")
                        continue

                    local_path = os.path.join(local_dir, filename)
                    logger.info(f"Downloading {filename} -> {local_path}")

                    with open(local_path, 'wb') as f:
                        ftp.retrbinary(f"RETR {filename}", f.write)

                    downloaded_files.append(local_path)
                    logger.debug(f"Successfully downloaded {filename}")

                if not downloaded_files:
                    logger.warning("No files matched the specified file_types filter.")
                else:
                    logger.info(f"Downloaded {len(downloaded_files)} files successfully")

                return downloaded_files

        except ftplib.error_perm as e:
            logger.error(f"FTP permission error: {str(e)}")
            if "530" in str(e):
                logger.error("Invalid credentials. Check username/password.")
            break  # Don't retry on permission errors
        except Exception as e:
            attempt += 1
            logger.error(f"Attempt {attempt}/{retries} failed: {str(e)}")
            if attempt < retries:
                logger.info(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                logger.critical("Maximum retry attempts reached")
                break

    # If we reach here, either all retries failed or a fatal error occurred
    logger.error("FTP download failed or no files downloaded after all attempts.")
    return []
