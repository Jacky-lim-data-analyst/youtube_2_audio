"""YouTube video downloader CLI
Downloads YouTube videos in its highest available resolution"""

from pytubefix import YouTube
from pytubefix.cli import on_progress
from pathlib import Path
import sys
import argparse

def download_video(url, output_dir=None, filename=None, max_retries=3):
    """
    Download a YouTube video.
    
    Args:
        url: YouTube video URL
        output_dir: Directory to save the video (default: ./data/video_files)
        filename: Output filename (default: video title with .mp4)
        max_retries: Maximum download retry attempts"""
    try:
        print("Fetching video from YouTube...")
        yt = YouTube(url, on_progress_callback=on_progress)
        print(f"Title: {yt.title}")
        print(f"Duration: {yt.length}s")
        print(f"Author: {yt.author}")

        ys = yt.streams.get_highest_resolution()
        if not ys:
            print("Error: No streams available for this video", file=sys.stderr)
            return False
        
        print(f"Resolution: {ys.resolution}")
        print(f"File size: ~{ys.filesize_mb:.2f} MB")

        # set output directory
        if output_dir is None:
            output_dir = Path() / "data" / "video_files"
        else:
            output_dir = Path(output_dir)

        output_dir.mkdir(parents=True, exist_ok=True)

        # set filename
        if filename is None:
            # remove problematic characters and use video title
            safe_title = str(yt.title).split(".")[0]
            # replace characters that might cause filesystem issues
            for char in ['/', '\\', ':', '*', '?', '"', '<', '>', "|"]:
                safe_title = safe_title.replace(char, '_')
            filename = f"{safe_title}.mp4"
        else:
            if ".mp4" not in filename.lower():
                filename += ".mp4"

        if len(filename) > 255:
            filename = filename[:255]

        print(f"\nDownload to {output_dir / filename}")
        ys.download(
            output_path=output_dir,
            filename=filename,
            max_retries=max_retries
        )

        print("\nDownload completed")
        print(f'Saved to {output_dir / filename}')
        return True
    except Exception as ex:
        print(f"Error: {ex}", file=sys.stderr)
        return False

def main():
    parser = argparse.ArgumentParser(
        description="Download YouTube videos in highest resolution",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
        Examples:
        %(prog)s "<url>"
        %(prog)s "<url>" -o ~/Downloads
        %(prog)s "<url>" -f "my_video.mp4"
        """
    )

    parser.add_argument(
        "url",
        help="YouTube video URL"
    )

    parser.add_argument(
        "-o", "--output-dir",
        help="Output directory (default: ./data/video_files)",
        default=None
    )

    parser.add_argument(
        "-f", "--filename",
        help="Output filename (default: video title + .mp4)",
        default=None
    )

    parser.add_argument(
        "-r", "--max-retries",
        type=int,
        help="Maximum download retry attempts (default:3)",
        default=3
    )

    args = parser.parse_args()

    success = download_video(
        url=args.url,
        output_dir=args.output_dir,
        filename=args.filename,
        max_retries=args.max_retries
    )

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
