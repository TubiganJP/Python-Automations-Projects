
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

DOWNLOAD_DIR = BASE_DIR / "downloads"

VIDEO_FORMAT = "bestvideo*+bestaudio/best"

MERGE_FORMAT = "mp4"

PLAYLIST = False

OVERWRITE = False
