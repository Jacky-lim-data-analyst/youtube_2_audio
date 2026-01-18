from pytubefix import YouTube
from pytubefix.cli import on_progress
from pathlib import Path
import sys

url = "https://www.youtube.com/watch?v=4wMhXxZ1zNM"

yt = YouTube(url, on_progress_callback=on_progress)
print(yt.title)

ys = yt.streams.get_highest_resolution()
if not ys:
    print("Stream class is None")
    sys.exit(1)

output_dir = Path() / "video_files"
output_filename = str(yt.title).split(".")[0] + ".mp4"
ys.download(
    output_path=output_dir,
    filename=output_filename,
    max_retries=3
)
