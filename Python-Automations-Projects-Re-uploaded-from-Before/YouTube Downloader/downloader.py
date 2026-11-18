
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError

from config import DOWNLOAD_DIR, VIDEO_FORMAT, MERGE_FORMAT, PLAYLIST, OVERWRITE


def progress_hook(data):
    if data["status"] == "downloading":
        percentage = data.get("_percent_str", "N/A")
        speed = data.get("_speed_str", "N/A")
        eta = data.get("_eta_str", "N/A")

        print(
            f"\rDownloading: {percentage} | Speed: {speed} | ETA: {eta}",
            end="",
            flush=True
        )

    elif data["status"] == "finished":
        print("\nDownload finished. Processing video...")


def download_video(url):
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

    options = {
        "format": VIDEO_FORMAT,
        "outtmpl": str(DOWNLOAD_DIR / "%(title)s.%(ext)s"),
        "noplaylist": not PLAYLIST,
        "nooverwrites": not OVERWRITE,
        "windowsfilenames": True,
        "progress_hooks": [progress_hook],
        "merge_output_format": MERGE_FORMAT,
    }

    try:
        with YoutubeDL(options) as ydl:
            ydl.download([url])

    except DownloadError as error:
        print(f"\nDownload failed: {error}")
