import os
import time
import signal
import threading
import logging
from queue import Queue
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from prometheus_client import start_http_server, Counter, Summary

# Configure logging
logging.basicConfig(
    filename="file_reorg_daemon.log",
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Prometheus Metrics
FILES_PROCESSED = Counter('files_processed_total', 'Total number of files processed')
PROCESSING_TIME = Summary('file_processing_seconds', 'Time spent processing files')
FILE_QUEUE_SIZE = Counter('file_queue_size', 'Current number of files in queue')

# Configuration
WATCH_DIRECTORY = "/path/to/watch"
DESTINATION_DIRECTORY = "/path/to/destination"
MAX_WORKERS = 4

# Queue for processing
file_queue = Queue()

def process_file(file_path):
    """Process a single file with error handling."""
    start_time = time.time()
    try:
        destination_path = os.path.join(DESTINATION_DIRECTORY, os.path.basename(file_path))
        os.rename(file_path, destination_path)
        FILES_PROCESSED.inc()
        logging.info(f"Moved {file_path} to {destination_path}")
    except Exception as e:
        logging.error(f"Error processing {file_path}: {e}")
    finally:
        PROCESSING_TIME.observe(time.time() - start_time)

def worker():
    """Worker function to process files from queue."""
    while True:
        file_path = file_queue.get()
        if file_path is None:
            break
        process_file(file_path)
        file_queue.task_done()

def monitor_directory():
    """Monitors a directory and adds new files to the queue."""
    class Handler(FileSystemEventHandler):
        def on_created(self, event):
            if not event.is_directory:
                logging.info(f"New file detected: {event.src_path}")
                FILE_QUEUE_SIZE.inc()
                file_queue.put(event.src_path)
    
    observer = Observer()
    observer.schedule(Handler(), WATCH_DIRECTORY, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

def signal_handler(sig, frame):
    """Handles shutdown signals gracefully."""
    logging.info("Shutdown signal received. Exiting...")
    for _ in range(MAX_WORKERS):
        file_queue.put(None)
    exit(0)

if __name__ == "__main__":
    start_http_server(8000)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start worker threads
    for _ in range(MAX_WORKERS):
        threading.Thread(target=worker, daemon=True).start()
    
    # Start monitoring directory
    monitor_directory()
