
import csv
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from statistics import mean


# Configuration
LOG_FOLDER = Path("E:/System Monitoring")

SYSTEM_LOG = LOG_FOLDER / "system_metrics.csv"
PROCESS_LOG = LOG_FOLDER / "process_metrics.csv"


# Read CSV data
def read_csv(file_path):
    if not file_path.exists():
        print(f"File not found: {file_path}")
        return []

    try:
        with open(file_path, "r", newline="", encoding="utf-8") as file:
            return list(csv.DictReader(file))

    except OSError as error:
        print(f"Unable to read {file_path}: {error}")
        return []


# Convert CSV values to numbers
def get_number(row, column):
    try:
        return float(row[column])
    except (KeyError, ValueError, TypeError):
        return None


# Calculate basic statistics
def calculate_statistics(values):
    values = [value for value in values if value is not None]

    if not values:
        return None

    return {
        "average": mean(values),
        "minimum": min(values),
        "maximum": max(values)
    }


# Display statistics
def display_statistics(title, values, unit="%"):
    stats = calculate_statistics(values)

    print(f"\n{title}")

    if stats is None:
        print("No recorded data available.")
        return

    print(f"  Average: {stats['average']:.2f}{unit}")
    print(f"  Minimum: {stats['minimum']:.2f}{unit}")
    print(f"  Maximum: {stats['maximum']:.2f}{unit}")


# Remove duplicated system samples
def get_unique_system_samples(rows):
    samples = {}

    for row in rows:
        timestamp = row.get("Timestamp")

        if timestamp and timestamp not in samples:
            samples[timestamp] = row

    return list(samples.values())


# Analyze monitoring duration
def analyze_duration(rows):
    timestamps = []

    for row in rows:
        timestamp = row.get("Timestamp")

        if not timestamp:
            continue

        try:
            timestamps.append(
                datetime.fromisoformat(timestamp)
            )
        except ValueError:
            continue

    if not timestamps:
        return None, 0

    start_time = min(timestamps)
    end_time = max(timestamps)

    duration = end_time - start_time

    return duration, len(set(timestamps))


# Analyze disk usage
def analyze_disks(rows):
    disk_data = defaultdict(list)

    for row in rows:
        drive = row.get("Drive")

        if not drive:
            continue

        usage = get_number(row, "Disk Usage (%)")

        if usage is not None:
            disk_data[drive].append(usage)

    print("\nDISK USAGE")

    if not disk_data:
        print("No recorded disk data available.")
        return

    for drive, values in sorted(disk_data.items()):
        stats = calculate_statistics(values)

        print(f"\n  Drive: {drive}")
        print(f"    Average: {stats['average']:.2f}%")
        print(f"    Minimum: {stats['minimum']:.2f}%")
        print(f"    Maximum: {stats['maximum']:.2f}%")


# Analyze top processes
def analyze_processes(rows):
    process_data = defaultdict(lambda: {
        "cpu": [],
        "memory": []
    })

    for row in rows:
        pid = row.get("PID")
        name = row.get("Process Name")

        if not pid or not name:
            continue

        process_key = (pid, name)

        cpu = get_number(row, "CPU Usage (%)")
        memory = get_number(row, "Memory Usage (MB)")

        if cpu is not None:
            process_data[process_key]["cpu"].append(cpu)

        if memory is not None:
            process_data[process_key]["memory"].append(memory)

    print("\nTOP PROCESSES BY CPU USAGE")

    if not process_data:
        print("No recorded process data available.")
        return

    cpu_processes = []

    for (pid, name), values in process_data.items():
        if values["cpu"]:
            cpu_processes.append((
                max(values["cpu"]),
                pid,
                name
            ))

    for usage, pid, name in sorted(
        cpu_processes, reverse=True
    )[:5]:
        print(f"  {name} (PID {pid}): {usage:.2f}%")

    print("\nTOP PROCESSES BY MEMORY USAGE")

    memory_processes = []

    for (pid, name), values in process_data.items():
        if values["memory"]:
            memory_processes.append((
                max(values["memory"]),
                pid,
                name
            ))

    for usage, pid, name in sorted(
        memory_processes, reverse=True
    )[:5]:
        print(f"  {name} (PID {pid}): {usage:.2f} MB")


# Main analysis
def main():
    print("=" * 55)
    print("       SYSTEM PERFORMANCE ANALYZER")
    print("=" * 55)

    system_rows = read_csv(SYSTEM_LOG)
    process_rows = read_csv(PROCESS_LOG)

    if not system_rows and not process_rows:
        print("\nNo monitoring data available.")
        print("Run system_monitor.py first to generate logs.")
        return

    unique_samples = get_unique_system_samples(system_rows)

    # Monitoring overview
    duration, sample_count = analyze_duration(unique_samples)

    print("\nMONITORING OVERVIEW")
    print(f"  System samples: {sample_count}")

    if duration is not None:
        print(f"  Monitoring duration: {duration}")

    # CPU statistics
    display_statistics(
        "CPU USAGE",
        [
            get_number(row, "CPU Usage (%)")
            for row in unique_samples
        ]
    )

    # RAM statistics
    display_statistics(
        "RAM USAGE",
        [
            get_number(row, "RAM Usage (%)")
            for row in unique_samples
        ]
    )

    # Disk statistics
    analyze_disks(system_rows)

    # Network statistics
    display_statistics(
        "UPLOAD SPEED",
        [
            get_number(row, "Upload Speed (KB/s)")
            for row in unique_samples
        ],
        " KB/s"
    )

    display_statistics(
        "DOWNLOAD SPEED",
        [
            get_number(row, "Download Speed (KB/s)")
            for row in unique_samples
        ],
        " KB/s"
    )

    # Process statistics
    analyze_processes(process_rows)

    print("\n" + "=" * 55)
    print("       ANALYSIS COMPLETED")
    print("=" * 55)


if __name__ == "__main__":
    main()
