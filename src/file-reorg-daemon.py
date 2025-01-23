import argparse
import os
import re
import shutil
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# Regex pattern for date-based file naming
RE_FILENAME_WITH_DATE = re.compile(r'^([0-9]{4})-([0-9]{2})-([0-9]{2})')
ERROR_THRESHOLD = 5.0 # Number of errors after which to raise alerting on

# Logging configuration (log level can be set via environment variable)
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=log_level, format='%(asctime)s - %(levelname)s - %(message)s')

class FileSyncManager:
    """Manages file checking, moving, and monitoring for performance and reliability."""

    def __init__(self, source, destination, quarantine_folder, poll_interval, max_workers=4, max_retries=3):
        self.source = source
        self.destination = destination
        self.quarantine_folder = quarantine_folder
        self.poll_interval = poll_interval / 1000  # Convert milliseconds to seconds
        self.max_retries = max_retries
        self.processed_files = set()  # Track processed files
        self.max_workers = max_workers

        # Performance and reliability metrics
        self.success_count = 0
        self.failure_count = 0
        self.total_processing_time = 0
        self.start_time = time.time()

    def run(self):
        """Continuously polls the source directory and processes new files."""
        logging.info("Starting file synchronization process...")
        while True:
            if self.check_disk_space():
                self.process_files()
                self.log_metrics()  # Log ongoing performance metrics
            else:
                logging.warning("Low disk space! Skipping file processing until resolved.")
            time.sleep(self.poll_interval)  

    def process_files(self):
        """Processes all files in the source directory using a thread pool"""
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            for filename in os.listdir(self.source):
                src_path = os.path.join(self.source, filename)
                # To avoid unecessary processing we check if it is a file and if it has been processed already
                if os.path.isfile(src_path) and not self.is_file_processed(src_path):
                    if RE_FILENAME_WITH_DATE.match(filename):
                        # Add file to thread pool to be processed
                        # Store result as a future object (i.e. the pending result)
                        futures.append(executor.submit(self.move_file_with_retry, src_path))

            # Track completed tasks and capture performance for each
            for future in as_completed(futures):
                future.result()  # If task raised an exception it will be propgated here

    def is_file_processed(self, src_path):
        """Checks if a file has been processed."""
        return src_path in self.processed_files

    def mark_as_processed(self, src_path):
        """Marks a file as processed."""
        self.processed_files.add(src_path)

    def move_file_with_retry(self, src_path):
        """Moves file to the destination with retry logic and exponential backoff."""
        attempts = 0
        while attempts < self.max_retries:
            try:
                start_time = time.time()
                self.move_file(src_path)
                elapsed_time = time.time() - start_time
                self.success_count += 1
                self.total_processing_time += elapsed_time # Record metrics
                logging.info(f"File {src_path} moved in {elapsed_time:.2f} seconds")
                self.mark_file_as_processed(src_path)  # If successful, mark file as processed
                return
            except Exception as e:
                attempts += 1
                logging.warning(f"Attempt {attempts} to move {src_path} failed: {e}")
                time.sleep(2 ** attempts)  # Exponential backoff to avoid rapid consecutive retries

        # Move to quarantine if all retries fail
        self.quarantine_file(src_path)

    def move_file(self, src_path):
        """Moves the file to a date-organized structure in the destination directory."""
        date_match = RE_FILENAME_WITH_DATE.match(os.path.basename(src_path))
        if date_match:
            year, month, day = date_match.groups()
            dest_path = os.path.join(self.destination, year, month, day)
            os.makedirs(dest_path, exist_ok=True)
            shutil.move(src_path, os.path.join(dest_path, os.path.basename(src_path)))
            logging.info(f"Moved {src_path} to {dest_path}")

    def quarantine_file(self, src_path):
        """Moves problematic files to a quarantine folder after repeated failures."""
        os.makedirs(self.quarantine_folder, exist_ok=True)
        quarantine_path = os.path.join(self.quarantine_folder, os.path.basename(src_path))
        shutil.move(src_path, quarantine_path)
        self.failure_count += 1
        logging.error(f"Moved {src_path} to quarantine after {self.max_retries} failed attempts")

    def check_disk_space(self):
        """Checks for adequate disk space in the destination and quarantine directories."""
        total, used, free = shutil.disk_usage(self.destination)
        return free / total > 0.1  # Ensure at least 10% disk space is available

    def log_metrics(self):
        """Logs performance metrics and checks against SLA thresholds."""
        current_time = time.time()
        elapsed_time = current_time - self.start_time

        # Calculate metrics
        total_files = self.success_count + self.failure_count
        avg_time_per_file = self.total_processing_time / self.success_count if self.success_count else 0
        error_rate = (self.failure_count / total_files) * 100 if total_files else 0
        throughput = self.success_count / elapsed_time if elapsed_time > 0 else 0

        # Log metrics
        logging.info(
            f"Metrics - Processed: {total_files}, Success: {self.success_count}, "
            f"Failures: {self.failure_count}, Avg Time/File: {avg_time_per_file:.2f}s, "
            f"Error Rate: {error_rate:.2f}%, Throughput: {throughput:.2f} files/sec"
        )

        # Alert if error rate exceeds threshold
        if error_rate > ERROR_THRESHOLD:
            logging.warning("High error rate detected! Immediate attention required.")
        
        # Reset metrics periodically for ongoing tracking
        if elapsed_time > 3600:  # Reset metrics every hour
            self.start_time = current_time
            self.success_count = 0
            self.failure_count = 0
            self.total_processing_time = 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="File reorganizer daemon with enhancements.")
    parser.add_argument("source", type=str, help="Source directory to monitor")
    parser.add_argument("destination", type=str, help="Root destination directory for files")
    parser.add_argument("quarantine_folder", type=str, help="Folder to quarantine problematic files")
    parser.add_argument("--poll_interval", type=int, default=5000, help="Polling interval in milliseconds")
    parser.add_argument("--max_workers", type=int, default=4, help="Maximum number of threads for concurrent processing")
    parser.add_argument("--max_retries", type=int, default=3, help="Maximum number of retry attempts for each file")
    args = parser.parse_args()

    manager = FileSyncManager(
        source=args.source,
        destination=args.destination,
        quarantine_folder=args.quarantine_folder,
        poll_interval=args.poll_interval,
        max_workers=args.max_workers,
        max_retries=args.max_retries,
    )
    manager.run()
