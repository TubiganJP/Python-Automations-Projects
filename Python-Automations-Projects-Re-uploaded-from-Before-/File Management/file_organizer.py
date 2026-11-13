
import time
import shutil
from pathlib import Path


DOWNLOAD_FOLDER = Path.home() / "Downloads"

STABLE_SECONDS = 3

# ==========================================
# FILE CATEGORIES
# ==========================================

FILE_CATEGORIES = {

    # Images and photographs
    "Images": [
        ".jpg", ".jpeg", ".png", ".gif",
        ".bmp", ".webp", ".svg", ".ico",
        ".tiff", ".tif", ".heic", ".heif",
        ".raw", ".cr2", ".nef", ".arw",
        ".dng", ".avif"
    ],

    # Documents
    "Documents": [
        ".pdf", ".doc", ".docx", ".txt",
        ".rtf", ".odt", ".wps"
    ],

    # Spreadsheets
    "Spreadsheets": [
        ".xls", ".xlsx", ".xlsm", ".csv",
        ".ods", ".tsv"
    ],

    # Presentations
    "Presentations": [
        ".ppt", ".pptx", ".pptm",
        ".odp", ".key"
    ],

    # Markdown documentation and notes
    "Markdown": [
        ".md", ".markdown", ".mdown",
        ".mkd", ".mdx", ".rmd"
    ],

    # Machine Learning and AI model files
    "Machine Learning Models": [
        ".pt", ".pth", ".ptl",
        ".onnx", ".h5", ".hdf5",
        ".pb", ".tflite", ".keras",
        ".safetensors", ".ckpt",
        ".pkl", ".pickle", ".joblib",
        ".model", ".weights",
        ".engine", ".mlmodel",
        ".gguf", ".ggml"
    ],

    # Machine Learning datasets and data files
    "Datasets": [
        ".parquet", ".feather", ".arrow",
        ".npy", ".npz", ".mat",
        ".jsonl", ".ndjson",
        ".pklz"
    ],

    # Jupyter notebooks and data science files
    "Data Science & Notebooks": [
        ".ipynb", ".r", ".rds",
        ".rdata"
    ],

    # Videos
    "Videos": [
        ".mp4", ".mkv", ".avi", ".mov",
        ".wmv", ".flv", ".webm", ".mpeg",
        ".mpg", ".m4v", ".3gp"
    ],

    # Audio
    "Audio": [
        ".mp3", ".wav", ".flac", ".aac",
        ".ogg", ".m4a", ".wma", ".aiff"
    ],

    # Compressed files
    "Archives": [
        ".zip", ".rar", ".7z", ".tar",
        ".gz", ".bz2", ".xz",
        ".tgz", ".zst"
    ],

    # Software installers
    "Installers": [
        ".exe", ".msi", ".apk",
        ".deb", ".dmg", ".iso",
        ".appx", ".msix"
    ],

    # Programming source code
    "Code": [
        ".py", ".js", ".ts", ".jsx",
        ".tsx", ".html", ".css", ".scss",
        ".php", ".java", ".cpp", ".c",
        ".cs", ".go", ".rs", ".rb",
        ".swift", ".kt", ".dart",
        ".vue", ".svelte", ".sql",
        ".sh", ".bat", ".ps1"
    ],

    # Configuration and structured data
    "Data & Configuration": [
        ".json", ".xml", ".yaml", ".yml",
        ".toml", ".ini", ".cfg",
        ".conf", ".env"
    ],

    # Database files
    "Database": [
        ".db", ".sqlite", ".sqlite3",
        ".mdb", ".accdb"
    ],

    # E-books
    "Ebooks": [
        ".epub", ".mobi", ".azw",
        ".azw3", ".djvu"
    ],

    # Fonts
    "Fonts": [
        ".ttf", ".otf", ".woff",
        ".woff2", ".eot"
    ],

    # Design and 3D files
    "Design & 3D": [
        ".psd", ".ai", ".eps", ".sketch",
        ".fig", ".blend", ".fbx",
        ".obj", ".stl", ".glb", ".gltf"
    ]
}

# Temporary download extensions
TEMP_EXTENSIONS = [
    ".crdownload",
    ".part",
    ".tmp"
]

# Track files being downloaded
file_tracker = {}


# ==========================================
# DETERMINE FILE CATEGORY
# ==========================================

def get_category(file_path):

    extension = file_path.suffix.lower()

    for category, extensions in FILE_CATEGORIES.items():

        if extension in extensions:
            return category

    return "Others"


# ==========================================
# PREVENT FILE OVERWRITING
# ==========================================

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


def organize_file(file_path):

    try:

        category = get_category(file_path)

        target_folder = DOWNLOAD_FOLDER / category

        # Create folder if it doesn't exist
        target_folder.mkdir(exist_ok=True)

        destination = get_unique_destination(
            target_folder / file_path.name
        )

        # Move file
        shutil.move(
            str(file_path),
            str(destination)
        )

        print(
            f"[MOVED] {file_path.name} "
            f"-> {category}/"
        )

    except (PermissionError, OSError) as error:

        print(
            f"[ERROR] {file_path.name}: {error}"
        )


# ==========================================
# MONITOR DOWNLOADS FOLDER
# ==========================================

def monitor_downloads():

    print("======================================")
    print("       SMART FILE ORGANIZER")
    print("======================================")

    print(f"Monitoring: {DOWNLOAD_FOLDER}")
    print("Status: RUNNING")
    print("Press CTRL + C to stop.")
    print("--------------------------------------")

    while True:

        for file_path in DOWNLOAD_FOLDER.iterdir():

            # Ignore folders
            if not file_path.is_file():
                continue

            # Ignore incomplete downloads
            if file_path.suffix.lower() in TEMP_EXTENSIONS:
                continue

            try:

                current_size = file_path.stat().st_size
                current_time = time.time()

                # First time detecting the file
                if file_path not in file_tracker:

                    file_tracker[file_path] = {
                        "size": current_size,
                        "last_change": current_time
                    }

                    continue

                previous = file_tracker[file_path]

                # Check whether file size changed
                if current_size != previous["size"]:

                    file_tracker[file_path] = {
                        "size": current_size,
                        "last_change": current_time
                    }

                    continue

                # Calculate how long file has been unchanged
                stable_time = (
                    current_time -
                    previous["last_change"]
                )

                # Organize once download is complete
                if stable_time >= STABLE_SECONDS:

                    organize_file(file_path)

                    file_tracker.pop(
                        file_path,
                        None
                    )

            except FileNotFoundError:

                file_tracker.pop(
                    file_path,
                    None
                )

            except PermissionError:

                continue

        time.sleep(1)



if __name__ == "__main__":

    try:

        monitor_downloads()

    except KeyboardInterrupt:

        print("\nFile Organizer stopped.")
