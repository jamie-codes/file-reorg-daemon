# File Reorganization Daemon

Author: Jamie McKee

## Overview
The **File Reorganization Daemon** is a Python-based service that continuously monitors a target directory for new files and automatically moves them into a structured destination directory. This daemon is optimized for **performance, scalability, logging, and monitoring** to be suitable for production environments.

## Features
- **Multi-threaded Processing**: Uses worker threads to handle file moves concurrently.
- **Queue-Based Management**: Ensures efficient handling of multiple incoming files.
- **Robust Logging**: Logs important events and errors in a structured format.
- **Prometheus Monitoring**: Exposes key metrics for real-time observability.
- **Graceful Shutdown Handling**: Ensures proper cleanup and termination.
- **Configurable Directory Watching**: Uses `watchdog` to monitor file events efficiently.

## Installation & Setup
### Prerequisites
Ensure you have the following dependencies installed:
```bash
pip install watchdog prometheus-client
```

### Configuration
Modify the script to specify the directories:
```python
WATCH_DIRECTORY = "/path/to/watch"
DESTINATION_DIRECTORY = "/path/to/destination"
MAX_WORKERS = 4
```

## Running the Daemon
Start the daemon by running:
```bash
python file-reorg-daemon.py
```

### Monitoring with Prometheus
The daemon exposes a Prometheus metrics endpoint at:
```
http://localhost:8000/metrics
```
Metrics available:
- `files_processed_total`: Total number of files moved.
- `file_processing_seconds`: Time spent processing each file.
- `file_queue_size`: Number of files currently in the processing queue.

## Logging
Logs are stored in `file_reorg_daemon.log` with structured information for easy debugging and tracking.

## Stopping the Daemon
Use `CTRL+C` or send a termination signal:
```bash
kill -SIGTERM <process_id>
```
The daemon handles shutdown signals gracefully.

## Contributing
If you want to enhance this daemon, feel free to fork and submit a pull request!

## License
This project is open-source and available under the MIT License.

