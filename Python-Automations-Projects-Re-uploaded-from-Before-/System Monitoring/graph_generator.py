
import csv
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt


# Configuration
LOG_FOLDER = Path("E:/System Monitoring")
GRAPH_FOLDER = LOG_FOLDER / "graphs"

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


# Convert CSV values
def get_number(row, column):
    try:
        return float(row[column])
    except (KeyError, ValueError, TypeError):
        return None


# Parse timestamps
def get_timestamp(row):
    try:
        return datetime.fromisoformat(row["Timestamp"])
    except (KeyError, ValueError, TypeError):
        return None


# Remove duplicate system samples
def get_unique_samples(rows):
    samples = {}

    for row in rows:
        timestamp = row.get("Timestamp")

        if timestamp and timestamp not in samples:
            samples[timestamp] = row

    sorted_samples = sorted(
        samples.values(),
        key=lambda row: get_timestamp(row)
    )

    return sorted_samples


# Prepare graph folder
def create_graph_folder():
    GRAPH_FOLDER.mkdir(parents=True, exist_ok=True)


# Generate CPU and RAM graph
def generate_cpu_ram_graph(rows):
    timestamps = []
    cpu_values = []
    ram_values = []

    for row in rows:
        timestamp = get_timestamp(row)
        cpu = get_number(row, "CPU Usage (%)")
        ram = get_number(row, "RAM Usage (%)")

        if timestamp is None or cpu is None or ram is None:
            continue

        timestamps.append(timestamp)
        cpu_values.append(cpu)
        ram_values.append(ram)

    if not timestamps:
        print("No CPU and RAM data available.")
        return

    plt.figure(figsize=(12, 6))

    plt.plot(
        timestamps,
        cpu_values,
        marker="o",
        label="CPU Usage (%)"
    )

    plt.plot(
        timestamps,
        ram_values,
        marker="o",
        label="RAM Usage (%)"
    )

    plt.title("CPU and RAM Usage Over Time")
    plt.xlabel("Timestamp")
    plt.ylabel("Usage (%)")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=30)
    plt.tight_layout()

    output_path = GRAPH_FOLDER / "cpu_ram_usage.png"
    plt.savefig(output_path, dpi=150)
    plt.close()

    print(f"Generated: {output_path}")


# Generate disk usage graph
def generate_disk_graph(rows):
    disk_data = defaultdict(list)

    for row in rows:
        drive = row.get("Drive")
        usage = get_number(row, "Disk Usage (%)")

        if drive and usage is not None:
            disk_data[drive].append(usage)

    if not disk_data:
        print("No disk data available.")
        return

    drives = sorted(disk_data.keys())
    average_usage = [
        sum(disk_data[drive]) / len(disk_data[drive])
        for drive in drives
    ]

    plt.figure(figsize=(9, 6))

    bars = plt.bar(drives, average_usage)

    plt.title("Average Disk Usage by Drive")
    plt.xlabel("Drive")
    plt.ylabel("Average Usage (%)")
    plt.ylim(0, 100)
    plt.grid(axis="y", alpha=0.3)

    for bar, value in zip(bars, average_usage):
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"{value:.2f}%",
            ha="center",
            va="bottom"
        )

    plt.tight_layout()

    output_path = GRAPH_FOLDER / "disk_usage.png"
    plt.savefig(output_path, dpi=150)
    plt.close()

    print(f"Generated: {output_path}")


# Generate network activity graph
def generate_network_graph(rows):
    timestamps = []
    upload_values = []
    download_values = []

    for row in rows:
        timestamp = get_timestamp(row)
        upload = get_number(row, "Upload Speed (KB/s)")
        download = get_number(row, "Download Speed (KB/s)")

        if timestamp is None or upload is None or download is None:
            continue

        timestamps.append(timestamp)
        upload_values.append(upload)
        download_values.append(download)

    if not timestamps:
        print("No network data available.")
        return

    plt.figure(figsize=(12, 6))

    plt.plot(
        timestamps,
        upload_values,
        marker="o",
        label="Upload Speed"
    )

    plt.plot(
        timestamps,
        download_values,
        marker="o",
        label="Download Speed"
    )

    plt.title("Network Activity Over Time")
    plt.xlabel("Timestamp")
    plt.ylabel("Speed (KB/s)")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=30)
    plt.tight_layout()

    output_path = GRAPH_FOLDER / "network_activity.png"
    plt.savefig(output_path, dpi=150)
    plt.close()

    print(f"Generated: {output_path}")


# Generate top processes graph
def generate_process_graph(rows):
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

    cpu_processes = []
    memory_processes = []

    for (pid, name), values in process_data.items():
        if values["cpu"]:
            cpu_processes.append((
                max(values["cpu"]),
                f"{name} (PID {pid})"
            ))

        if values["memory"]:
            memory_processes.append((
                max(values["memory"]),
                f"{name} (PID {pid})"
            ))

    cpu_processes = sorted(
        cpu_processes, reverse=True
    )[:5]

    memory_processes = sorted(
        memory_processes, reverse=True
    )[:5]

    if not cpu_processes and not memory_processes:
        print("No process data available.")
        return

    figure, axes = plt.subplots(1, 2, figsize=(16, 7))

    if cpu_processes:
        cpu_processes.reverse()

        axes[0].barh(
            [item[1] for item in cpu_processes],
            [item[0] for item in cpu_processes]
        )

        axes[0].set_title("Top Processes by CPU Usage")
        axes[0].set_xlabel("CPU Usage (%)")
        axes[0].grid(axis="x", alpha=0.3)

    if memory_processes:
        memory_processes.reverse()

        axes[1].barh(
            [item[1] for item in memory_processes],
            [item[0] for item in memory_processes]
        )

        axes[1].set_title("Top Processes by Memory Usage")
        axes[1].set_xlabel("Memory Usage (MB)")
        axes[1].grid(axis="x", alpha=0.3)

    figure.tight_layout()

    output_path = GRAPH_FOLDER / "top_processes.png"
    figure.savefig(output_path, dpi=150)
    plt.close(figure)

    print(f"Generated: {output_path}")


# Main graph generation
def main():
    print("=" * 55)
    print("       SYSTEM PERFORMANCE GRAPH GENERATOR")
    print("=" * 55)

    create_graph_folder()

    system_rows = read_csv(SYSTEM_LOG)
    process_rows = read_csv(PROCESS_LOG)

    unique_samples = get_unique_samples(system_rows)

    if not unique_samples and not process_rows:
        print("\nNo monitoring data available.")
        print("Run system_monitor.py first to generate logs.")
        return

    print("\nGenerating performance graphs...\n")

    generate_cpu_ram_graph(unique_samples)
    generate_disk_graph(system_rows)
    generate_network_graph(unique_samples)
    generate_process_graph(process_rows)

    print("\n" + "=" * 55)
    print("       GRAPH GENERATION COMPLETED")
    print("=" * 55)


if __name__ == "__main__":
    main()
