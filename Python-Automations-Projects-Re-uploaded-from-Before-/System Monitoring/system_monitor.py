import csv
import platform
import socket
import time
from datetime import datetime
from pathlib import Path

import psutil


# Monitoring settings
MONITOR_INTERVAL = 5
LOG_FOLDER = Path("E:/System Monitoring")

CPU_THRESHOLD = 80
RAM_THRESHOLD = 85
DISK_THRESHOLD = 90

TOP_PROCESSES = 5

MONITOR_CPU = True
MONITOR_RAM = True
MONITOR_DISK = True
MONITOR_NETWORK = True
MONITOR_PROCESSES = True

SAVE_LOGS = True
SHOW_ALERTS = True


# Log file paths
SYSTEM_LOG = LOG_FOLDER / "system_metrics.csv"
PROCESS_LOG = LOG_FOLDER / "process_metrics.csv"


# Get basic computer information
def get_system_info():
    return {
        "hostname": socket.gethostname(),
        "operating_system": platform.system(),
        "os_version": platform.version(),
        "processor": platform.processor()
    }


# Get CPU information
def get_cpu_info():
    cpu_usage = psutil.cpu_percent(interval=None)
    cpu_frequency = psutil.cpu_freq()

    return {
        "usage": cpu_usage,
        "frequency": round(cpu_frequency.current, 2) if cpu_frequency else 0,
        "physical_cores": psutil.cpu_count(logical=False),
        "logical_cores": psutil.cpu_count(logical=True)
    }


# Get memory information
def get_memory_info():
    memory = psutil.virtual_memory()

    return {
        "total": round(memory.total / (1024 ** 3), 2),
        "used": round(memory.used / (1024 ** 3), 2),
        "available": round(memory.available / (1024 ** 3), 2),
        "percentage": memory.percent
    }


# Get disk information
def get_disk_info():
    disks = []

    for partition in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(partition.mountpoint)

            disks.append({
                "drive": partition.device,
                "total": round(usage.total / (1024 ** 3), 2),
                "used": round(usage.used / (1024 ** 3), 2),
                "free": round(usage.free / (1024 ** 3), 2),
                "percentage": usage.percent
            })

        except (PermissionError, OSError):
            continue

    return disks


# Calculate network upload and download speeds
def get_network_info(previous_network, elapsed_time):
    current_network = psutil.net_io_counters()

    upload_speed = 0
    download_speed = 0

    if previous_network and elapsed_time > 0:
        upload_speed = (
            current_network.bytes_sent - previous_network.bytes_sent
        ) / elapsed_time

        download_speed = (
            current_network.bytes_recv - previous_network.bytes_recv
        ) / elapsed_time

    return {
        "total_sent": round(current_network.bytes_sent / (1024 ** 2), 2),
        "total_received": round(current_network.bytes_recv / (1024 ** 2), 2),
        "upload_speed": round(upload_speed / 1024, 2),
        "download_speed": round(download_speed / 1024, 2),
        "current_network": current_network
    }


# Get the top processes by CPU and memory usage

# Get the top processes by CPU and memory usage
def get_process_info():
    processes = []
    logical_cores = psutil.cpu_count(logical=True) or 1

    for process in psutil.process_iter(
        ["pid", "name", "memory_info"]
    ):
        try:
            process_info = process.info

            if process_info["pid"] == 0:
                continue

            memory_info = process_info["memory_info"]

            cpu_usage = process.cpu_percent(interval=None)
            cpu_usage = round(cpu_usage / logical_cores, 2)

            processes.append({
                "pid": process_info["pid"],
                "name": process_info["name"] or "Unknown",
                "cpu": cpu_usage,
                "memory": round(
                    memory_info.rss / (1024 ** 2), 2
                ) if memory_info else 0
            })

        except (
            psutil.NoSuchProcess,
            psutil.AccessDenied,
            psutil.ZombieProcess
        ):
            continue

    top_cpu = sorted(
        processes,
        key=lambda process: process["cpu"],
        reverse=True
    )[:TOP_PROCESSES]

    top_memory = sorted(
        processes,
        key=lambda process: process["memory"],
        reverse=True
    )[:TOP_PROCESSES]

    return top_cpu, top_memory



# Check resource usage against configured thresholds
def check_thresholds(cpu_info, memory_info, disks):
    if not SHOW_ALERTS:
        return

    if MONITOR_CPU and cpu_info["usage"] >= CPU_THRESHOLD:
        print(
            f"WARNING: CPU usage is high: {cpu_info['usage']}%"
        )

    if MONITOR_RAM and memory_info["percentage"] >= RAM_THRESHOLD:
        print(
            f"WARNING: RAM usage is high: {memory_info['percentage']}%"
        )

    if MONITOR_DISK:
        for disk in disks:
            if disk["percentage"] >= DISK_THRESHOLD:
                print(
                    f"WARNING: Disk {disk['drive']} usage is high: "
                    f"{disk['percentage']}%"
                )


# Save system statistics to CSV
def save_system_log(timestamp, system_info, cpu_info, memory_info,
                    disks, network_info):

    if not SAVE_LOGS:
        return

    LOG_FOLDER.mkdir(parents=True, exist_ok=True)

    file_exists = SYSTEM_LOG.exists() and SYSTEM_LOG.stat().st_size > 0

    with SYSTEM_LOG.open("a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow([
                "Timestamp",
                "Hostname",
                "Operating System",
                "OS Version",
                "Processor",
                "CPU Usage (%)",
                "CPU Frequency (MHz)",
                "Physical Cores",
                "Logical Cores",
                "Total RAM (GB)",
                "Used RAM (GB)",
                "Available RAM (GB)",
                "RAM Usage (%)",
                "Drive",
                "Total Disk (GB)",
                "Used Disk (GB)",
                "Free Disk (GB)",
                "Disk Usage (%)",
                "Total Sent (MB)",
                "Total Received (MB)",
                "Upload Speed (KB/s)",
                "Download Speed (KB/s)"
            ])

        for disk in disks:
            writer.writerow([
                timestamp,
                system_info["hostname"],
                system_info["operating_system"],
                system_info["os_version"],
                system_info["processor"],
                cpu_info["usage"] if MONITOR_CPU else "",
                cpu_info["frequency"] if MONITOR_CPU else "",
                cpu_info["physical_cores"] if MONITOR_CPU else "",
                cpu_info["logical_cores"] if MONITOR_CPU else "",
                memory_info["total"] if MONITOR_RAM else "",
                memory_info["used"] if MONITOR_RAM else "",
                memory_info["available"] if MONITOR_RAM else "",
                memory_info["percentage"] if MONITOR_RAM else "",
                disk["drive"] if MONITOR_DISK else "",
                disk["total"] if MONITOR_DISK else "",
                disk["used"] if MONITOR_DISK else "",
                disk["free"] if MONITOR_DISK else "",
                disk["percentage"] if MONITOR_DISK else "",
                network_info["total_sent"] if MONITOR_NETWORK else "",
                network_info["total_received"] if MONITOR_NETWORK else "",
                network_info["upload_speed"] if MONITOR_NETWORK else "",
                network_info["download_speed"] if MONITOR_NETWORK else ""
            ])


# Save process information to CSV
def save_process_log(timestamp, top_cpu, top_memory):
    if not SAVE_LOGS or not MONITOR_PROCESSES:
        return

    LOG_FOLDER.mkdir(parents=True, exist_ok=True)

    file_exists = PROCESS_LOG.exists() and PROCESS_LOG.stat().st_size > 0

    with PROCESS_LOG.open("a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow([
                "Timestamp",
                "Category",
                "PID",
                "Process Name",
                "CPU Usage (%)",
                "Memory Usage (MB)"
            ])

        for category, processes in [
            ("Top CPU", top_cpu),
            ("Top Memory", top_memory)
        ]:
            for process in processes:
                writer.writerow([
                    timestamp,
                    category,
                    process["pid"],
                    process["name"],
                    process["cpu"],
                    process["memory"]
                ])


# Display monitoring results in PowerShell
def display_system_info(system_info, cpu_info, memory_info,
                        disks, network_info, top_cpu, top_memory):

    print("\n" + "=" * 60)
    print("SYSTEM MONITORING")
    print("=" * 60)

    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Computer: {system_info['hostname']}")
    print(
        f"Operating System: {system_info['operating_system']} "
        f"{system_info['os_version']}"
    )

    if MONITOR_CPU:
        print("\nCPU")
        print(f"Usage: {cpu_info['usage']}%")
        print(f"Frequency: {cpu_info['frequency']} MHz")
        print(f"Physical Cores: {cpu_info['physical_cores']}")
        print(f"Logical Cores: {cpu_info['logical_cores']}")

    if MONITOR_RAM:
        print("\nMEMORY")
        print(f"Total: {memory_info['total']} GB")
        print(f"Used: {memory_info['used']} GB")
        print(f"Available: {memory_info['available']} GB")
        print(f"Usage: {memory_info['percentage']}%")

    if MONITOR_DISK:
        print("\nDISK")

        for disk in disks:
            print(
                f"{disk['drive']} | "
                f"Used: {disk['used']} GB | "
                f"Free: {disk['free']} GB | "
                f"Usage: {disk['percentage']}%"
            )

    if MONITOR_NETWORK:
        print("\nNETWORK")
        print(f"Total Sent: {network_info['total_sent']} MB")
        print(f"Total Received: {network_info['total_received']} MB")
        print(f"Upload Speed: {network_info['upload_speed']} KB/s")
        print(f"Download Speed: {network_info['download_speed']} KB/s")

    if MONITOR_PROCESSES:
        print("\nTOP CPU PROCESSES")

        for process in top_cpu:
            print(
                f"{process['name']} (PID: {process['pid']}) | "
                f"CPU: {process['cpu']}%"
            )

        print("\nTOP MEMORY PROCESSES")

        for process in top_memory:
            print(
                f"{process['name']} (PID: {process['pid']}) | "
                f"Memory: {process['memory']} MB"
            )

    print("=" * 60)


# Run the monitoring program
def main():
    print("Starting System Monitoring...")
    print("Press Ctrl + C to stop monitoring.")

    system_info = get_system_info()

    previous_network = None
    previous_time = None

    try:
        while True:
            current_time = time.time()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            cpu_info = get_cpu_info() if MONITOR_CPU else {}
            memory_info = get_memory_info() if MONITOR_RAM else {}
            disks = get_disk_info() if MONITOR_DISK else []

            elapsed_time = (
                current_time - previous_time
                if previous_time is not None else 0
            )

            network_info = (
                get_network_info(previous_network, elapsed_time)
                if MONITOR_NETWORK else {}
            )

            top_cpu, top_memory = (
                get_process_info()
                if MONITOR_PROCESSES else ([], [])
            )

            display_system_info(
                system_info,
                cpu_info,
                memory_info,
                disks,
                network_info,
                top_cpu,
                top_memory
            )

            if MONITOR_CPU or MONITOR_RAM or MONITOR_DISK:
                check_thresholds(cpu_info, memory_info, disks)

            save_system_log(
                timestamp,
                system_info,
                cpu_info,
                memory_info,
                disks,
                network_info
            )

            save_process_log(timestamp, top_cpu, top_memory)

            if MONITOR_NETWORK:
                previous_network = network_info["current_network"]

            previous_time = current_time

            time.sleep(MONITOR_INTERVAL)

    except KeyboardInterrupt:
        print("\nSystem Monitoring stopped.")

    except Exception as error:
        print(f"\nAn unexpected error occurred: {error}")


if __name__ == "__main__":
    main()