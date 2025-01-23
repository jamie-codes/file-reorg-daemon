# File Reorganizer Daemon

`file-reorg-daemon.py` is a Python script designed to monitor a source directory for new files, reorganize them into a date-based folder structure within a destination directory, and handle errors gracefully by quarantining problematic files. It supports concurrent processing and provides detailed logging and performance metrics.

---

## Features

- **Date-based File Organization**: Files named with a `YYYY-MM-DD` format are sorted into a structured directory hierarchy (`/destination/YYYY/MM/DD/`).
- **Error Handling**: Files that fail to process after multiple retries are moved to a quarantine folder.
- **Concurrency**: Supports multi-threaded file processing with configurable worker threads.
- **Metrics Logging**: Tracks processing performance, including success/failure rates and average processing time.
- **Polling**: Continuously monitors the source directory for new files with a configurable polling interval.
- **Disk Space Check**: Skips processing when disk space is below a safe threshold.

---

## Installation

Ensure you have Python 3.6+ installed. Clone the repository containing the script:

```bash
git clone https://github.com/your-repo/file-reorg-daemon.git
cd file-reorg-daemon/src
```

---

## Usage

Run the script from the command line:

```bash
python file-reorg-daemon.py <source> <destination> <quarantine_folder> [options]
```

### Required Arguments

- `source`: Path to the source directory to monitor for new files.
- `destination`: Root path for reorganized files.
- `quarantine_folder`: Path to store problematic files.

### Optional Arguments

- `--poll_interval`: Polling interval in milliseconds (default: 5000 ms).
- `--max_workers`: Maximum number of threads for concurrent processing (default: 4).
- `--max_retries`: Number of retries for failed file operations (default: 3).

### Example

```bash
python file-reorg-daemon.py /path/to/source /path/to/destination /path/to/quarantine --poll_interval 3000 --max_workers 6 --max_retries 5
```

---

## Logging

The script logs its operations to the console. You can configure the log level using the `LOG_LEVEL` environment variable:

```bash
export LOG_LEVEL=DEBUG  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
```

Example log output:

```
2025-01-22 10:00:00 - INFO - Starting file synchronization process...
2025-01-22 10:00:05 - INFO - File /path/to/source/2025-01-21-example.txt moved in 0.35 seconds
2025-01-22 10:00:05 - ERROR - Moved /path/to/source/problematic.txt to quarantine after 3 failed attempts
```

---

## Key Functionalities

### File Organization

Files are moved to directories structured by their date:

```
/destination/YYYY/MM/DD/
```

### Quarantine Handling

Files failing after all retries are moved to the specified quarantine folder for further inspection.

### Performance Metrics

Periodic logs provide insight into:

- Total processed files
- Success and failure counts
- Average processing time per file
- Error rate
- Throughput (files processed per second)

### Disk Space Monitoring

The script ensures at least 10% free disk space is available in the destination before processing.

---

## Development

### Dependencies

No external dependencies are required; all functionality relies on Python's standard library.

### Testing

You can test the script by creating sample files in the source directory and observing the behaviour in the destination and quarantine folders.

---

## Contributing

If you'd like to contribute:

1. Fork the repository.
2. Create a feature branch.
3. Submit a pull request.

---

