
from downloader import download_video


def main():
    print("=" * 40)
    print("       YOUTUBE VIDEO DOWNLOADER")
    print("=" * 40)

    while True:
        print("\n[1] Download Video")
        print("[2] Exit")

        choice = input("\nEnter your choice: ").strip()

        if choice == "1":
            url = input("\nEnter YouTube URL: ").strip()

            if not url:
                print("Please enter a valid URL.")
                continue

            download_video(url)

        elif choice == "2":
            print("\nExiting YouTube Downloader. Goodbye!")
            break

        else:
            print("\nInvalid choice. Please try again.")


if __name__ == "__main__":
    main()
