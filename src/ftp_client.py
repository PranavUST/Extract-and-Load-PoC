import ftplib
import os
import logging
import time

logger = logging.getLogger(__name__)

def download_ftp_files(host, username, password, remote_dir, local_dir, file_types=None, retries=3, delay=5):
    """
    Download files from an FTP server to a local directory, with retry logic.
    file_types: list of file extensions to download (e.g., ['.csv', '.json', '.parquet'])
    retries: number of retry attempts (default 3)
    delay: seconds to wait between retries (default 5)
    """
    attempt = 0
    while attempt < retries:
        try:
            os.makedirs(local_dir, exist_ok=True)
            with ftplib.FTP(host) as ftp:
                ftp.login(user=username, passwd=password)
                ftp.cwd(remote_dir)
                files = ftp.nlst()
                for filename in files:
                    if file_types and not any(filename.lower().endswith(ext) for ext in file_types):
                        continue
                    local_path = os.path.join(local_dir, filename)
                    with open(local_path, 'wb') as f:
                        ftp.retrbinary(f"RETR {filename}", f.write)
                    logger.info(f"Downloaded: {filename} to {local_path}")
            return  # Success, exit the function
        except Exception as e:
            attempt += 1
            logger.error(f"FTP download failed (attempt {attempt}/{retries}): {e}")
            if attempt < retries:
                time.sleep(delay)
            else:
                logger.error("Max FTP retries reached. Raising exception.")
                raise