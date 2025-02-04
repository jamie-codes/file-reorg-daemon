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

=======
# File Reorg Daemon

## Overview
The File Reorg Daemon is a Python script that monitors a source directory and automatically moves files to a structured date-based directory format. It supports dynamic quarantine handling, a configurable retry mechanism, and enhanced logging with log rotation.

## Features
- **Automatic File Organization**: Moves files based on their last modified date.
- **Configuration via YAML**: Easily adjustable parameters without modifying the script.
- **Quarantine Handling**: Files that fail multiple move attempts are quarantined.
- **Enhanced Logging**: Supports log rotation and different log levels.
- **Retry Mechanism**: Allows multiple attempts before quarantining a file.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/jamie-codes/file-reorg-daemon.git
   cd file-reorg-daemon
   ```

2. Install dependencies (if needed):
   ```bash
   pip install -r requirements.txt
   ```

3. Configure the daemon by editing `config.yaml`.

## Configuration
The script reads settings from `config.yaml`. Below is an example configuration:

```yaml
source_directory: "/path/to/source"
destination_directory: "/path/to/destination"
quarantine_directory: "/path/to/quarantine"
log_file: "file_reorg.log"
debug_mode: true
retry_attempts: 3
```

### Explanation of Configuration Parameters:
- `source_directory`: Directory where the script monitors for files.
- `destination_directory`: Base directory where organized files are stored.
- `quarantine_directory`: Directory where files are moved if they fail multiple move attempts.
- `log_file`: Path to the log file for tracking script activity.
- `debug_mode`: Enables verbose logging when set to `true`.
- `retry_attempts`: Number of times the script attempts to move a file before quarantining it.

## Usage
Run the script manually:

```bash
python file-reorg-daemon.py
```

Or schedule it as a cron job:

```bash
*/5 * * * * /usr/bin/python3 /path/to/file-reorg-daemon.py
```

## Logging
Logs are stored in the file specified in `config.yaml`. The script uses a rotating log system, ensuring old logs are archived when the file size exceeds 1MB.

To view logs in real time:

```bash
tail -f file_reorg.log
```

## Quarantine Handling
If a file cannot be moved after the specified number of retries, it is automatically placed in the quarantine directory for manual review.

## License
This project is licensed under the MIT License.

## Contributing
Feel free to fork the repository and submit pull requests with improvements or bug fixes.
