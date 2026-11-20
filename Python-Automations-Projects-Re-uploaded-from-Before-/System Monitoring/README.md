# System Monitoring Automation

A Python-based system monitoring tool that tracks computer performance and resource usage in real time. It collects CPU, memory, disk, network, and running process information using the `psutil` library.

The project also includes historical performance analysis, graphical visualizations, HTML report generation, and desktop notifications to provide a more comprehensive view of system performance.

## Features

### Real-Time System Monitoring

- **CPU Monitoring** - Tracks CPU utilization, frequency, physical cores, and logical processors.
- **Memory Monitoring** - Displays total, used, and available RAM.
- **Disk Monitoring** - Tracks storage usage and available space across detected drives.
- **Network Monitoring** - Measures total network traffic and upload/download speeds.
- **Process Monitoring** - Identifies the top processes consuming CPU and memory.
- **Threshold Alerts** - Displays warnings when CPU, RAM, or disk usage exceeds configured limits.
- **Desktop Notifications** - Sends Windows desktop notifications when resource usage exceeds configured thresholds, with a notification cooldown.
- **CSV Logging** - Saves historical system and process monitoring records.
- **Continuous Monitoring** - Collects information at configurable intervals until manually stopped.

### Performance Analysis and Reporting

- **Historical Performance Analysis** - Calculates average, minimum, and maximum resource usage from recorded monitoring data.
- **Performance Graphs** - Generates graphs for CPU and RAM usage, disk usage, network activity, and top processes.
- **HTML Monitoring Report** - Generates a standalone HTML report containing performance summaries, process information, and embedded graphs.

## Requirements

- Python 3.10 or later
- psutil
- matplotlib
- plyer

Install the required libraries:

```bash
pip install psutil matplotlib plyer
```

## Project Structure

```text
System Monitoring/
├── system_monitor.py
├── performance_analyzer.py
├── graph_generator.py
├── report_generator.py
├── notification_manager.py
└── README.md
```

## Configuration

The monitoring settings can be modified directly in `system_monitor.py`.

| Parameter                  |              Default | Description                                                 |
| -------------------------- | -------------------: | ----------------------------------------------------------- |
| MONITOR_INTERVAL           |                    5 | Monitoring interval in seconds                              |
| LOG_FOLDER                 | E:/System Monitoring | Directory for CSV logs                                      |
| CPU_THRESHOLD              |                   80 | CPU warning threshold (%)                                   |
| RAM_THRESHOLD              |                   85 | RAM warning threshold (%)                                   |
| DISK_THRESHOLD             |                   90 | Disk warning threshold (%)                                  |
| TOP_PROCESSES              |                    5 | Number of top processes displayed                           |
| MONITOR_CPU                |                 True | Enable CPU monitoring                                       |
| MONITOR_RAM                |                 True | Enable RAM monitoring                                       |
| MONITOR_DISK               |                 True | Enable disk monitoring                                      |
| MONITOR_NETWORK            |                 True | Enable network monitoring                                   |
| MONITOR_PROCESSES          |                 True | Enable process monitoring                                   |
| SAVE_LOGS                  |                 True | Enable CSV logging                                          |
| SHOW_ALERTS                |                 True | Enable console warnings                                     |
| SHOW_DESKTOP_NOTIFICATIONS |                 True | Enable desktop notifications                                |
| NOTIFICATION_COOLDOWN      |                  300 | Minimum seconds between notifications for the same resource |

## How to Run

Navigate to the project directory:

```powershell
cd "E:\Python Automations\Python-Automations-Projects-Re-uploaded-from-Before-\System Monitoring"
```

### 1. Start System Monitoring

```bash
python system_monitor.py
```

The program continuously collects and displays system performance information.

To stop monitoring, press:

```text
Ctrl + C
```

### 2. Analyze Historical Performance

```bash
python performance_analyzer.py
```

Generates historical performance summaries, including average, minimum, and maximum resource usage.

### 3. Generate Performance Graphs

```bash
python graph_generator.py
```

Generates visualizations based on the collected monitoring data.

### 4. Generate HTML Report

```bash
python report_generator.py
```

Creates a standalone HTML monitoring report containing performance summaries, process information, and embedded graphs.

## Generated Logs and Reports

CSV logs, graphs, and reports are automatically saved in the configured output directory:

```text
E:/
└── System Monitoring/
    ├── system_metrics.csv
    ├── process_metrics.csv
    ├── graphs/
    │   ├── cpu_ram_usage.png
    │   ├── disk_usage.png
    │   ├── network_activity.png
    │   └── top_processes.png
    └── system_report.html
```

### Generated Files

- `system_metrics.csv` - Contains system performance measurements, including CPU, RAM, disk, and network statistics.
- `process_metrics.csv` - Contains records of the top CPU- and memory-consuming processes.
- `graphs/` - Stores generated performance visualization images.
- `system_report.html` - Contains the generated HTML performance report.

## Technologies Used

- Python
- psutil
- Matplotlib
- Plyer
- CSV
- HTML and CSS
- pathlib
- datetime

## Notes

- Process CPU percentages are normalized against the number of logical processors.
- Network speeds are calculated using traffic differences between monitoring intervals.
- Disk information depends on accessible mounted partitions.
- CPU and process measurements may require an initial sampling interval.
- Desktop notifications use Plyer and include a cooldown to prevent repeated notifications.
- The program only monitors system activity and does not terminate processes or modify system settings.
- Generated logs, graphs, and reports are stored outside the project directory by default.

## Future Enhancements

- CPU temperature monitoring.
- GPU temperature monitoring.
- Hardware sensor integration.
- Additional performance metrics and reporting capabilities.
