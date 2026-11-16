# System Monitoring Automation

A Python-based system monitoring tool that tracks computer performance and resource usage in real time. It collects CPU, memory, disk, network, and running process information using the `psutil` library.

## Features

- **CPU Monitoring** – Tracks CPU utilization, frequency, physical cores, and logical processors.
- **Memory Monitoring** – Displays total, used, and available RAM.
- **Disk Monitoring** – Tracks storage usage and available space across detected drives.
- **Network Monitoring** – Measures total network traffic and upload/download speeds.
- **Process Monitoring** – Identifies the top processes consuming CPU and memory.
- **Threshold Alerts** – Displays warnings when CPU, RAM, or disk usage exceeds configured limits.
- **CSV Logging** – Saves historical system and process monitoring records.
- **Continuous Monitoring** – Collects information at configurable intervals until manually stopped.

## Requirements

- Python 3.10 or later
- psutil

Install the required library:

```bash
pip install psutil
```

## Project Structure

```text
System Monitoring/
├── system_monitor.py
└── README.md
```

## Configuration

The monitoring settings can be modified directly in `system_monitor.py`.

| Parameter         |              Default | Description                       |
| ----------------- | -------------------: | --------------------------------- |
| MONITOR_INTERVAL  |                    5 | Monitoring interval in seconds    |
| LOG_FOLDER        | E:/System Monitoring | Directory for CSV logs            |
| CPU_THRESHOLD     |                   80 | CPU warning threshold (%)         |
| RAM_THRESHOLD     |                   85 | RAM warning threshold (%)         |
| DISK_THRESHOLD    |                   90 | Disk warning threshold (%)        |
| TOP_PROCESSES     |                    5 | Number of top processes displayed |
| MONITOR_CPU       |                 True | Enable CPU monitoring             |
| MONITOR_RAM       |                 True | Enable RAM monitoring             |
| MONITOR_DISK      |                 True | Enable disk monitoring            |
| MONITOR_NETWORK   |                 True | Enable network monitoring         |
| MONITOR_PROCESSES |                 True | Enable process monitoring         |
| SAVE_LOGS         |                 True | Enable CSV logging                |
| SHOW_ALERTS       |                 True | Enable console warnings           |

## How to Run

Navigate to the project directory and execute:

```bash
python system_monitor.py
```

The program will continuously collect and display system performance information.

To stop monitoring, press:

```text
Ctrl + C
```

## Generated Logs

CSV files are automatically created in the configured log directory.

```text
E:/
└── System Monitoring/
    ├── system_metrics.csv
    └── process_metrics.csv
```

- `system_metrics.csv` – Contains system performance measurements, including CPU, RAM, disk, and network statistics.
- `process_metrics.csv` – Contains records of the top CPU- and memory-consuming processes.

## Technologies Used

- Python
- psutil
- CSV
- pathlib
- datetime

## Notes

- Process CPU percentages are normalized against the number of logical processors.
- Network speeds are calculated using traffic differences between monitoring intervals.
- Disk information depends on accessible mounted partitions.
- CPU and process measurements may require an initial sampling interval.
- The program only monitors system activity and does not terminate processes or modify system settings.
