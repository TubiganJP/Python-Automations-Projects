
import csv
import hashlib
import shutil
from pathlib import Path
from collections import defaultdict

# File settings
TARGET_FOLDER = Path.home() / "Downloads"
DUPLICATES_FOLDER = TARGET_FOLDER / "Duplicate Files"
REPORT_FILE = Path.home() / "duplicate_report.csv"

RECURSIVE = True
MIN_FILE_SIZE = 1
HASH_ALGORITHM = "sha256"
CHUNK_SIZE = 1024 * 1024


# Get files from the target folder
def get_files():

    files = []

    if not TARGET_FOLDER.exists():
        print("[ERROR] Target folder does not exist.")
        return files

    file_list = (
        TARGET_FOLDER.rglob("*")
        if RECURSIVE
        else TARGET_FOLDER.iterdir()
    )

    for file_path in file_list:

        if not file_path.is_file() or file_path.is_symlink():
            continue

        try:
            file_path.resolve().relative_to(
                DUPLICATES_FOLDER.resolve()
            )
            continue
        except ValueError:
            pass

        try:
            if file_path.stat().st_size >= MIN_FILE_SIZE:
                files.append(file_path)

        except OSError as error:
            print(f"[ERROR] {file_path.name}: {error}")

    return files


# Group files according to their sizes
def group_by_size(files):

    size_groups = defaultdict(list)

    for file_path in files:

        try:
            file_size = file_path.stat().st_size
            size_groups[file_size].append(file_path)

        except OSError as error:
            print(f"[ERROR] {file_path.name}: {error}")

    return size_groups


# Calculate the SHA-256 hash of a file
def calculate_hash(file_path):

    hasher = hashlib.new(HASH_ALGORITHM)

    try:

        initial_stat = file_path.stat()

        with open(file_path, "rb") as file:

            while True:

                chunk = file.read(CHUNK_SIZE)

                if not chunk:
                    break

                hasher.update(chunk)

        final_stat = file_path.stat()

        if (
            initial_stat.st_size != final_stat.st_size
            or initial_stat.st_mtime_ns != final_stat.st_mtime_ns
        ):
            print(f"[SKIPPED] File changed: {file_path.name}")
            return None

        return hasher.hexdigest()

    except OSError as error:
        print(f"[ERROR] {file_path.name}: {error}")
        return None


# Find files with identical contents
def find_duplicates(size_groups):

    hash_groups = defaultdict(list)

    for file_size, files in size_groups.items():

        if len(files) < 2:
            continue

        for file_path in files:

            file_hash = calculate_hash(file_path)

            if file_hash is None:
                continue

            hash_groups[(file_size, file_hash)].append(file_path)

    duplicate_groups = []

    for (file_size, file_hash), files in hash_groups.items():

        if len(files) > 1:

            files.sort(key=lambda path: str(path).casefold())

            duplicate_groups.append({
                "size": file_size,
                "hash": file_hash,
                "files": files
            })

    return duplicate_groups


# Prevent overwriting existing files
def get_unique_destination(destination):

    if not destination.exists():
        return destination

    counter = 1

    while True:

        new_name = (
            f"{destination.stem}_{counter}"
            f"{destination.suffix}"
        )

        new_destination = destination.with_name(new_name)

        if not new_destination.exists():
            return new_destination

        counter += 1


# Move duplicate files into the duplicates folder
def move_duplicates(duplicate_groups):

    report_data = []

    for group_number, group in enumerate(
        duplicate_groups, start=1
    ):

        original = group["files"][0]

        for duplicate in group["files"][1:]:

            try:

                relative_path = duplicate.relative_to(TARGET_FOLDER)

                destination_folder = (
                    DUPLICATES_FOLDER / relative_path.parent
                )

                destination_folder.mkdir(
                    parents=True,
                    exist_ok=True
                )

                destination = get_unique_destination(
                    destination_folder / duplicate.name
                )

                shutil.move(
                    str(duplicate),
                    str(destination)
                )

                print(f"[MOVED] {duplicate.name}")

                report_data.append({
                    "Group": group_number,
                    "Original File": str(original),
                    "Duplicate File": str(duplicate),
                    "Moved To": str(destination),
                    "File Size (Bytes)": group["size"],
                    "SHA256": group["hash"]
                })

            except OSError as error:

                print(f"[ERROR] {duplicate.name}: {error}")

    return report_data


# Save the results in a CSV file
def generate_report(report_data):

    fieldnames = [
        "Group",
        "Original File",
        "Duplicate File",
        "Moved To",
        "File Size (Bytes)",
        "SHA256"
    ]

    try:

        with open(
            REPORT_FILE,
            "w",
            newline="",
            encoding="utf-8-sig"
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=fieldnames
            )

            writer.writeheader()
            writer.writerows(report_data)

        print(f"\n[REPORT] Saved to: {REPORT_FILE}")

    except OSError as error:
        print(f"[ERROR] Could not generate report: {error}")


# Display the scan results
def display_results(duplicate_groups, report_data):

    total_groups = len(duplicate_groups)
    total_duplicates = len(report_data)

    total_size = sum(
        row["File Size (Bytes)"]
        for row in report_data
    )

    print("\n======================================")
    print("       DUPLICATE FILE FINDER")
    print("======================================")

    if not duplicate_groups:
        print("No duplicate files found.")

    else:

        for group_number, group in enumerate(
            duplicate_groups, start=1
        ):

            print(f"\nGroup {group_number}")
            print(f"Original: {group['files'][0]}")

            for duplicate in group["files"][1:]:
                print(f"Duplicate: {duplicate}")

        print("\n--------------------------------------")
        print(f"Duplicate Groups: {total_groups}")
        print(f"Duplicate Files Moved: {total_duplicates}")
        print(f"Potential Space Savings: {total_size:,} bytes")

    print("--------------------------------------")
    print("All duplicate files are preserved.")
    print("Scan completed.")


# Run the duplicate file finder
def main():

    print("======================================")
    print("       DUPLICATE FILE FINDER")
    print("======================================")

    print(f"Target Folder: {TARGET_FOLDER}")
    print(f"Recursive Scan: {RECURSIVE}")
    print(f"Hash Algorithm: {HASH_ALGORITHM}")

    print("\nScanning files...")

    files = get_files()

    print(f"Total Files Found: {len(files)}")

    print("\nGrouping files by size...")

    size_groups = group_by_size(files)

    print("Checking file contents...")

    duplicate_groups = find_duplicates(size_groups)

    print("\nMoving duplicate files...")

    report_data = move_duplicates(duplicate_groups)

    generate_report(report_data)

    display_results(duplicate_groups, report_data)


if __name__ == "__main__":

    try:
        main()

    except KeyboardInterrupt:
        print("\nProgram stopped by user.")
