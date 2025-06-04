import ftplib
import os
import logging

logger = logging.getLogger(__name__)

def download_ftp_files(host, username, password, remote_dir, local_dir, file_types=None):
    """
    Download files from an FTP server to a local directory.
    file_types: list of file extensions to download (e.g., ['.csv', '.json', '.parquet'])
    """
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