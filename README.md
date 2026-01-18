# yt-to-audio-files

A simple set of Python scripts to download audio from YouTube videos and convert M4A files to MP3 format.

## Prerequisites

- **Python 3.13+**
- **FFmpeg**: This tool is required for audio conversion. Ensure it is installed and available in your system's PATH.
    - Ubuntu/Debian: `sudo apt install ffmpeg`
    - macOS: `brew install ffmpeg`
    - Windows: Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH.

## Installation

This project uses `uv` for dependency management, but you can also install the requirements using pip.

### Using uv (Recommended)

```bash
uv sync
```

### Using pip

```bash
pip install pytubefix pedalboard
```

## Usage

### 1. Download Audio from YouTube

The `download_audio.py` script downloads the audio stream from a YouTube video.

```bash
python download_audio.py
```

*Note: Currently, the YouTube URL and output filename are hardcoded in the script. You may need to edit `url` and `filename` inside `download_audio.py` before running.*

### 2. Convert M4A to MP3

The `convert_m4a_2_mp3.py` script converts the downloaded M4A file to MP3 format using FFmpeg.

```bash
python convert_m4a_2_mp3.py
```

*Note: The input and output file paths are currently hardcoded. Edit the `source_file_path` and destination path in `convert_m4a_2_mp3.py` as needed.*

## Project Structure

- `download_audio.py`: Downloads audio using `pytubefix`.
- `convert_m4a_2_mp3.py`: Converts M4A to MP3 using `ffmpeg`.
- `audio_files/`: Directory for downloaded raw audio (M4A).
- `mp3_files/`: Directory for converted MP3 files.
