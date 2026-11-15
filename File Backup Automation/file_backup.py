
import csv
import hashlib
import json
import shutil
from datetime import datetime
from pathlib import Path

SOURCE_FOLDER = Path.home() / "Downloads"
BACKUP_FOLDER = Path("E:/Backups")

RECURSIVE = True
HASH_ALGORITHM = "sha256"
CHUNK_SIZE = 1024 * 1024

CREATE_TIMESTAMP_FOLDER = True
PRESERVE_FOLDER_STRUCTURE = True

MANIFEST_FILE = BACKUP_FOLDER / "backup_manifest.json"
REPORT_FILE = BACKUP_FOLDER / "backup_report.csv"

FILE_CATEGORIES = {
    "Images": {
        ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp",
        ".tiff", ".tif", ".heic", ".heif", ".svg", ".ico"
    },
    "Documents": {
        ".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt",
        ".md", ".markdown"
    },
    "Spreadsheets": {
        ".xls", ".xlsx", ".csv", ".ods"
    },
    "Presentations": {
        ".ppt", ".pptx", ".odp"
    },
    "Videos": {
        ".mp4", ".mkv", ".avi", ".mov", ".wmv", ".webm", ".flv"
    },
    "Audio": {
        ".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a", ".wma"
    },
    "Archives": {
        ".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"
    },
    "Code": {
        ".py", ".js", ".ts", ".html", ".css", ".php", ".java",
        ".cpp", ".c", ".cs", ".json", ".xml", ".sql", ".sh"
    },
    "Machine Learning Models": {
        ".pt", ".pth", ".ptl", ".onnx", ".h5", ".hdf5",
        ".pb", ".tflite", ".keras", ".safetensors", ".ckpt",
        ".pkl", ".pickle", ".joblib", ".model", ".weights",
        ".engine", ".mlmodel", ".gguf", ".ggml"
    },
    "Notebooks": {
        ".ipynb"
    },
    "Databases": {
        ".db", ".sqlite", ".sqlite3", ".mdb"
    },
    "Installers": {
        ".exe", ".msi", ".apk", ".dmg"
    },
    "Fonts": {
        ".ttf", ".otf", ".woff", ".woff2"
    }
}


# Load backup history
def load_manifest():
    if not MANIFEST_FILE.exists():
        return {"files": {}}

    try:
        with open(MANIFEST_FILE, "r", encoding="utf-8") as file:
            manifest = json.load(file)

        if not isinstance(manifest.get("files"), dict):
            raise ValueError("Invalid manifest format")

        return manifest

    except (json.JSONDecodeError, ValueError):
        print("Backup manifest is invalid. Please check the manifest file.")
        raise


# Save backup history
def save_manifest(manifest):
    BACKUP_FOLDER.mkdir(parents=True, exist_ok=True)

    with open(MANIFEST_FILE, "w", encoding="utf-8") as file:
        json.dump(manifest, file, indent=4)


# Get files from the source folder
def get_files():
    if not SOURCE_FOLDER.exists():
        raise FileNotFoundError(f"Source folder not found: {SOURCE_FOLDER}")

    if not SOURCE_FOLDER.is_dir():
        raise NotADirectoryError(f"Source path is not a folder: {SOURCE_FOLDER}")

    if not SOURCE_FOLDER.is_absolute() or not BACKUP_FOLDER.is_absolute():
        raise ValueError("Source and backup folders must use absolute paths.")

    source = SOURCE_FOLDER.resolve()
    backup = BACKUP_FOLDER.resolve()

    if source == backup or source in backup.parents:
        raise ValueError("Backup folder cannot be inside the source folder.")

    if backup in source.parents:
        raise ValueError("Source folder cannot be inside the backup folder.")

    if RECURSIVE:
        files = SOURCE_FOLDER.rglob("*")
    else:
        files = SOURCE_FOLDER.iterdir()

    file_list = []

    for file_path in files:
        if file_path.is_symlink() or not file_path.is_file():
            continue

        file_list.append(file_path)

    return file_list


# Identify file category
def get_category(file_path):
    extension = file_path.suffix.lower()

    for category, extensions in FILE_CATEGORIES.items():
        if extension in extensions:
            return category

    return "Other"


# Calculate file hash
def calculate_hash(file_path):
    hasher = hashlib.new(HASH_ALGORITHM)

    initial_stat = file_path.stat()

    with open(file_path, "rb") as file:
        while chunk := file.read(CHUNK_SIZE):
            hasher.update(chunk)

    final_stat = file_path.stat()

    if (
        initial_stat.st_size != final_stat.st_size
        or initial_stat.st_mtime_ns != final_stat.st_mtime_ns
    ):
        raise RuntimeError("File changed while being read.")

    return hasher.hexdigest()


# Generate backup filename
def create_backup_name(file_path, version):
    return f"{file_path.stem}_B{version}{file_path.suffix}"


# Get backup destination
def get_backup_destination(file_path, category, version, timestamp_folder):
    relative_path = file_path.relative_to(SOURCE_FOLDER)

    if PRESERVE_FOLDER_STRUCTURE:
        parent_folder = relative_path.parent
    else:
        parent_folder = Path()

    backup_name = create_backup_name(file_path, version)

    return timestamp_folder / category / parent_folder / backup_name


# Copy file into backup folder
def backup_file(file_path, destination, file_hash):
    destination.parent.mkdir(parents=True, exist_ok=True)

    shutil.copy2(file_path, destination)

    copied_hash = calculate_hash(destination)

    if copied_hash != file_hash:
        raise RuntimeError("Backup verification failed.")

    return destination


# Generate backup report
def generate_report(report_data):
    if not report_data:
        return

    BACKUP_FOLDER.mkdir(parents=True, exist_ok=True)

    file_exists = REPORT_FILE.exists()

    with open(REPORT_FILE, "a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "Backup Date",
                "Original File",
                "Backup File",
                "Category",
                "Version",
                "Status"
            ]
        )

        if not file_exists or REPORT_FILE.stat().st_size == 0:
            writer.writeheader()

        writer.writerows(report_data)


# Display backup results
def display_results(report_data):
    successful = sum(
        1 for item in report_data if item["Status"] == "Success"
    )

    failed = sum(
        1 for item in report_data if item["Status"] == "Failed"
    )

    print("\nBackup Summary")
    print("------------------------------")
    print(f"Files processed: {len(report_data)}")
    print(f"Successfully backed up: {successful}")
    print(f"Failed: {failed}")
    print(f"Backup location: {BACKUP_FOLDER}")
    print(f"Report location: {REPORT_FILE}")


# Main backup process
def main():
    BACKUP_FOLDER.mkdir(parents=True, exist_ok=True)

    manifest = load_manifest()
    files = get_files()

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    timestamp_folder = BACKUP_FOLDER / timestamp

    report_data = []
    updated_files = dict(manifest["files"])

    print(f"Scanning: {SOURCE_FOLDER}")
    print(f"Files found: {len(files)}")

    for file_path in files:
        source_key = str(file_path.resolve())

        try:
            file_hash = calculate_hash(file_path)
            previous = manifest["files"].get(source_key)

            if previous and previous["hash"] == file_hash:
                continue

            version = previous["version"] + 1 if previous else 1

            category = get_category(file_path)

            if CREATE_TIMESTAMP_FOLDER:
                destination_folder = timestamp_folder
            else:
                destination_folder = BACKUP_FOLDER

            destination = get_backup_destination(
                file_path,
                category,
                version,
                destination_folder
            )

            while destination.exists():
                version += 1
                destination = get_backup_destination(
                    file_path,
                    category,
                    version,
                    destination_folder
                )

            backup_file(file_path, destination, file_hash)

            updated_files[source_key] = {
                "hash": file_hash,
                "version": version
            }

            report_data.append({
                "Backup Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Original File": str(file_path),
                "Backup File": str(destination),
                "Category": category,
                "Version": f"B{version}",
                "Status": "Success"
            })

            print(f"Backed up: {file_path.name} -> B{version}")

        except (OSError, RuntimeError, ValueError) as error:
            report_data.append({
                "Backup Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Original File": str(file_path),
                "Backup File": "",
                "Category": get_category(file_path),
                "Version": "",
                "Status": f"Failed: {error}"
            })

            print(f"Failed: {file_path.name} - {error}")

    manifest["files"] = updated_files

    save_manifest(manifest)
    generate_report(report_data)
    display_results(report_data)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nBackup stopped by user.")
    except (OSError, ValueError, RuntimeError) as error:
        print(f"\nError: {error}")
