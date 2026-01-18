from pytubefix import YouTube
from pytubefix.cli import on_progress
from pathlib import Path

url = "https://www.youtube.com/watch?v=YuBcUiIls5E"
download_dir = Path() / "audio_files"

# make sure the path exists
download_dir.mkdir(parents=True, exist_ok=True)

yt = YouTube(url, on_progress_callback=on_progress)
print(yt.title)

ys = yt.streams.get_audio_only()
ys.download(
    output_path=str(download_dir),
    filename="eric_chou_duo_yuan_dou_yao_zai_yi_qi.m4a",
    max_retries=3
)
