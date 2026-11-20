
import base64
import csv
import html
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from statistics import mean


# Configuration
LOG_FOLDER = Path("E:/System Monitoring")
GRAPH_FOLDER = LOG_FOLDER / "graphs"

SYSTEM_LOG = LOG_FOLDER / "system_metrics.csv"
PROCESS_LOG = LOG_FOLDER / "process_metrics.csv"

REPORT_FILE = LOG_FOLDER / "system_report.html"


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


# Remove duplicated system samples
def get_unique_samples(rows):
    samples = {}

    for row in rows:
        timestamp = row.get("Timestamp")

        if timestamp and timestamp not in samples:
            samples[timestamp] = row

    return sorted(
        samples.values(),
        key=lambda row: get_timestamp(row)
    )


# Calculate statistics
def calculate_statistics(values):
    values = [value for value in values if value is not None]

    if not values:
        return None

    return {
        "average": mean(values),
        "minimum": min(values),
        "maximum": max(values)
    }


# Format statistics for HTML
def format_statistics(values, unit="%"):
    stats = calculate_statistics(values)

    if stats is None:
        return {
            "average": "N/A",
            "minimum": "N/A",
            "maximum": "N/A"
        }

    return {
        "average": f"{stats['average']:.2f}{unit}",
        "minimum": f"{stats['minimum']:.2f}{unit}",
        "maximum": f"{stats['maximum']:.2f}{unit}"
    }


# Embed graph images in HTML
def get_image_data(file_path):
    if not file_path.exists():
        print(f"Graph not found: {file_path}")
        return None

    try:
        with open(file_path, "rb") as file:
            encoded_image = base64.b64encode(
                file.read()
            ).decode("utf-8")

        return f"data:image/png;base64,{encoded_image}"

    except OSError as error:
        print(f"Unable to read graph: {error}")
        return None


# Generate monitoring overview
def generate_overview(rows):
    timestamps = [
        get_timestamp(row)
        for row in rows
    ]

    timestamps = [
        timestamp for timestamp in timestamps
        if timestamp is not None
    ]

    if not timestamps:
        return {
            "samples": 0,
            "start": "N/A",
            "end": "N/A",
            "duration": "N/A"
        }

    start_time = min(timestamps)
    end_time = max(timestamps)
    duration = end_time - start_time

    return {
        "samples": len(set(timestamps)),
        "start": start_time.strftime("%Y-%m-%d %H:%M:%S"),
        "end": end_time.strftime("%Y-%m-%d %H:%M:%S"),
        "duration": str(duration)
    }


# Generate disk statistics
def generate_disk_statistics(rows):
    disk_data = defaultdict(list)

    for row in rows:
        drive = row.get("Drive")
        usage = get_number(row, "Disk Usage (%)")

        if drive and usage is not None:
            disk_data[drive].append(usage)

    if not disk_data:
        return "<tr><td colspan='4'>No disk data available.</td></tr>"

    table_rows = []

    for drive, values in sorted(disk_data.items()):
        stats = calculate_statistics(values)

        table_rows.append(
            f"""
            <tr>
                <td>{html.escape(drive)}</td>
                <td>{stats['average']:.2f}%</td>
                <td>{stats['minimum']:.2f}%</td>
                <td>{stats['maximum']:.2f}%</td>
            </tr>
            """
        )

    return "\n".join(table_rows)


# Generate process statistics
def generate_process_statistics(rows):
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
                pid,
                name
            ))

        if values["memory"]:
            memory_processes.append((
                max(values["memory"]),
                pid,
                name
            ))

    cpu_processes.sort(reverse=True)
    memory_processes.sort(reverse=True)

    cpu_rows = []
    memory_rows = []

    for usage, pid, name in cpu_processes[:5]:
        cpu_rows.append(
            f"""
            <tr>
                <td>{html.escape(name)}</td>
                <td>{html.escape(pid)}</td>
                <td>{usage:.2f}%</td>
            </tr>
            """
        )

    for usage, pid, name in memory_processes[:5]:
        memory_rows.append(
            f"""
            <tr>
                <td>{html.escape(name)}</td>
                <td>{html.escape(pid)}</td>
                <td>{usage:.2f} MB</td>
            </tr>
            """
        )

    if not cpu_rows:
        cpu_rows.append(
            "<tr><td colspan='3'>No CPU process data available.</td></tr>"
        )

    if not memory_rows:
        memory_rows.append(
            "<tr><td colspan='3'>No memory process data available.</td></tr>"
        )

    return "\n".join(cpu_rows), "\n".join(memory_rows)


# Generate HTML graph section
def generate_graph_section():
    graphs = [
        ("CPU and RAM Usage", "cpu_ram_usage.png"),
        ("Disk Usage", "disk_usage.png"),
        ("Network Activity", "network_activity.png"),
        ("Top Processes", "top_processes.png")
    ]

    sections = []

    for title, filename in graphs:
        image_data = get_image_data(
            GRAPH_FOLDER / filename
        )

        if image_data:
            sections.append(
                f"""
                <div class="graph-card">
                    <h3>{title}</h3>
                    <img src="{image_data}" alt="{title}">
                </div>
                """
            )
        else:
            sections.append(
                f"""
                <div class="graph-card">
                    <h3>{title}</h3>
                    <p class="no-data">Graph image unavailable.</p>
                </div>
                """
            )

    return "\n".join(sections)


# Generate HTML report
def generate_html_report(system_rows, process_rows):
    unique_samples = get_unique_samples(system_rows)

    overview = generate_overview(unique_samples)

    cpu_stats = format_statistics(
        [
            get_number(row, "CPU Usage (%)")
            for row in unique_samples
        ]
    )

    ram_stats = format_statistics(
        [
            get_number(row, "RAM Usage (%)")
            for row in unique_samples
        ]
    )

    upload_stats = format_statistics(
        [
            get_number(row, "Upload Speed (KB/s)")
            for row in unique_samples
        ],
        " KB/s"
    )

    download_stats = format_statistics(
        [
            get_number(row, "Download Speed (KB/s)")
            for row in unique_samples
        ],
        " KB/s"
    )

    disk_rows = generate_disk_statistics(system_rows)

    cpu_process_rows, memory_process_rows = (
        generate_process_statistics(process_rows)
    )

    graph_sections = generate_graph_section()

    report_time = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>System Monitoring Report</title>

    <style>
        * {{
            box-sizing: border-box;
        }}

        body {{
            margin: 0;
            padding: 30px;
            background: #f1f5f9;
            color: #1e293b;
            font-family: Arial, sans-serif;
        }}

        .container {{
            max-width: 1250px;
            margin: auto;
        }}

        header {{
            padding: 30px;
            margin-bottom: 25px;
            background: #172554;
            color: white;
            border-radius: 12px;
        }}

        header h1 {{
            margin: 0 0 10px;
        }}

        header p {{
            margin: 5px 0;
            color: #cbd5e1;
        }}

        .section {{
            margin-bottom: 30px;
        }}

        .section h2 {{
            margin-bottom: 15px;
        }}

        .cards {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 15px;
        }}

        .card {{
            padding: 20px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        }}

        .card h3 {{
            margin: 0 0 12px;
            color: #475569;
            font-size: 15px;
        }}

        .value {{
            margin: 0 0 10px;
            font-size: 30px;
            font-weight: bold;
            color: #2563eb;
        }}

        .details {{
            color: #64748b;
            font-size: 13px;
            line-height: 1.8;
        }}

        .table-card {{
            padding: 20px;
            overflow-x: auto;
            background: white;
            border-radius: 10px;
            margin-bottom: 20px;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            text-align: left;
        }}

        th, td {{
            padding: 12px;
            border-bottom: 1px solid #e2e8f0;
        }}

        th {{
            background: #f8fafc;
            color: #475569;
        }}

        .graphs {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
        }}

        .graph-card {{
            padding: 20px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        }}

        .graph-card h3 {{
            margin-top: 0;
        }}

        .graph-card img {{
            width: 100%;
            height: auto;
        }}

        .no-data {{
            color: #64748b;
        }}

        footer {{
            padding: 20px;
            margin-top: 30px;
            text-align: center;
            color: #64748b;
            font-size: 13px;
        }}

        @media (max-width: 600px) {{
            body {{
                padding: 15px;
            }}

            .graphs {{
                grid-template-columns: 1fr;
            }}
        }}

        @media print {{
            body {{
                background: white;
                padding: 0;
            }}

            .card, .table-card, .graph-card {{
                box-shadow: none;
                border: 1px solid #ddd;
                break-inside: avoid;
            }}
        }}
    </style>
</head>

<body>
<div class="container">

    <header>
        <h1>System Monitoring Report</h1>
        <p>Historical System Performance Analysis</p>
        <p>Report generated: {report_time}</p>
    </header>

    <section class="section">
        <h2>Monitoring Overview</h2>

        <div class="cards">
            <div class="card">
                <h3>Total Samples</h3>
                <p class="value">{overview['samples']}</p>
                <div class="details">Unique monitoring timestamps</div>
            </div>

            <div class="card">
                <h3>Monitoring Duration</h3>
                <p class="value">{html.escape(overview['duration'])}</p>
                <div class="details">Recorded monitoring period</div>
            </div>

            <div class="card">
                <h3>First Recorded Sample</h3>
                <p class="details">{html.escape(overview['start'])}</p>
            </div>

            <div class="card">
                <h3>Last Recorded Sample</h3>
                <p class="details">{html.escape(overview['end'])}</p>
            </div>
        </div>
    </section>

    <section class="section">
        <h2>CPU and Memory Performance</h2>

        <div class="cards">
            <div class="card">
                <h3>CPU Usage</h3>
                <p class="value">{cpu_stats['average']}</p>
                <div class="details">
                    Minimum: {cpu_stats['minimum']}<br>
                    Maximum: {cpu_stats['maximum']}
                </div>
            </div>

            <div class="card">
                <h3>RAM Usage</h3>
                <p class="value">{ram_stats['average']}</p>
                <div class="details">
                    Minimum: {ram_stats['minimum']}<br>
                    Maximum: {ram_stats['maximum']}
                </div>
            </div>
        </div>
    </section>

    <section class="section">
        <h2>Network Performance</h2>

        <div class="cards">
            <div class="card">
                <h3>Average Upload Speed</h3>
                <p class="value">{upload_stats['average']}</p>
                <div class="details">
                    Minimum: {upload_stats['minimum']}<br>
                    Maximum: {upload_stats['maximum']}
                </div>
            </div>

            <div class="card">
                <h3>Average Download Speed</h3>
                <p class="value">{download_stats['average']}</p>
                <div class="details">
                    Minimum: {download_stats['minimum']}<br>
                    Maximum: {download_stats['maximum']}
                </div>
            </div>
        </div>
    </section>

    <section class="section">
        <h2>Disk Usage</h2>

        <div class="table-card">
            <table>
                <thead>
                    <tr>
                        <th>Drive</th>
                        <th>Average Usage</th>
                        <th>Minimum Usage</th>
                        <th>Maximum Usage</th>
                    </tr>
                </thead>
                <tbody>
                    {disk_rows}
                </tbody>
            </table>
        </div>
    </section>

    <section class="section">
        <h2>Top Processes by CPU Usage</h2>

        <div class="table-card">
            <table>
                <thead>
                    <tr>
                        <th>Process Name</th>
                        <th>PID</th>
                        <th>Maximum CPU Usage</th>
                    </tr>
                </thead>
                <tbody>
                    {cpu_process_rows}
                </tbody>
            </table>
        </div>
    </section>

    <section class="section">
        <h2>Top Processes by Memory Usage</h2>

        <div class="table-card">
            <table>
                <thead>
                    <tr>
                        <th>Process Name</th>
                        <th>PID</th>
                        <th>Maximum Memory Usage</th>
                    </tr>
                </thead>
                <tbody>
                    {memory_process_rows}
                </tbody>
            </table>
        </div>
    </section>

    <section class="section">
        <h2>Performance Graphs</h2>

        <div class="graphs">
            {graph_sections}
        </div>
    </section>

    <footer>
        Generated by Python System Monitoring Automation
    </footer>

</div>
</body>
</html>
"""


# Main report generation
def main():
    print("=" * 55)
    print("       SYSTEM MONITORING REPORT GENERATOR")
    print("=" * 55)

    system_rows = read_csv(SYSTEM_LOG)
    process_rows = read_csv(PROCESS_LOG)

    if not system_rows and not process_rows:
        print("\nNo monitoring data available.")
        print("Run system_monitor.py first to generate logs.")
        return

    report_content = generate_html_report(
        system_rows,
        process_rows
    )

    try:
        REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)

        with open(
            REPORT_FILE,
            "w",
            encoding="utf-8"
        ) as file:
            file.write(report_content)

        print("\nHTML report generated successfully!")
        print(f"Report location: {REPORT_FILE}")

    except OSError as error:
        print(f"\nUnable to generate report: {error}")
        return

    print("\n" + "=" * 55)
    print("       REPORT GENERATION COMPLETED")
    print("=" * 55)


if __name__ == "__main__":
    main()
