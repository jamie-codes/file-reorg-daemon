import os
import shutil
import logging
import time
import yaml
from logging.handlers import RotatingFileHandler

# Load configuration from a YAML file
def load_config(config_path="config.yaml"):
    with open(config_path, "r") as file:
        return yaml.safe_load(file)

config = load_config()

# Logging setup
log_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
log_handler = RotatingFileHandler(config["log_file"], maxBytes=1048576, backupCount=3)
log_handler.setFormatter(log_formatter)
logger = logging.getLogger("FileReorgDaemon")
logger.setLevel(logging.DEBUG if config["debug_mode"] else logging.INFO)
logger.addHandler(log_handler)

# Function to get file's modified time and categorize it
def get_date_folder(file_path):
    modified_time = time.gmtime(os.path.getmtime(file_path))
    return time.strftime("%Y-%m-%d", modified_time)

# Move files to their respective directories based on modification date
def move_files():
    source_dir = config["source_directory"]
    dest_dir = config["destination_directory"]
    quarantine_dir = config["quarantine_directory"]
    retry_attempts = config["retry_attempts"]
    
    if not os.path.exists(source_dir):
        logger.error(f"Source directory {source_dir} does not exist.")
        return
    
    for file_name in os.listdir(source_dir):
        file_path = os.path.join(source_dir, file_name)
        if not os.path.isfile(file_path):
            continue

        date_folder = get_date_folder(file_path)
        target_folder = os.path.join(dest_dir, date_folder)
        os.makedirs(target_folder, exist_ok=True)

        target_path = os.path.join(target_folder, file_name)
        attempts = 0

        while attempts < retry_attempts:
            try:
                shutil.move(file_path, target_path)
                logger.info(f"Moved {file_name} to {target_folder}")
                break
            except Exception as e:
                attempts += 1
                logger.warning(f"Attempt {attempts} failed for {file_name}: {e}")
                time.sleep(2)  # Wait before retrying
        else:
            quarantine_path = os.path.join(quarantine_dir, file_name)
            shutil.move(file_path, quarantine_path)
            logger.error(f"Quarantined {file_name} after {retry_attempts} failed attempts")

if __name__ == "__main__":
    move_files()
