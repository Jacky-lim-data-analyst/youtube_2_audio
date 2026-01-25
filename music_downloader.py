"""
YouTube Music Downloader CLI
A command line tool to download music from Youtube, convert formats and edit metadata
"""

import argparse
import subprocess
import sys
import requests
from pathlib import Path
from pytubefix import YouTube
# from pytubefix.cli import on_progress
from mutagen.mp4 import MP4, MP4Cover
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, TCON, TYER, APIC, USLT, TALB

def download_audio(url: str, output_dir: str | Path, filename: str | None = None):
    """Download audio from YouTube URL"""
    print(f"\nDownloading from: {url}")

    if isinstance(output_dir, str):
        output_path = Path(output_dir)
    
    output_path.mkdir(parents=True, exist_ok=True)

    yt = YouTube(url)
    print(f"Title: {yt.title}")

    stream = yt.streams.get_audio_only()

    if filename is None:
        # sanitize the title for use as filename
        safe_title = "".join(c for c in yt.title if c.isalnum() or c in (' ', '-', '_')).strip()
        filename = f"{safe_title}.m4a"
    else:
        filename = f"{filename}.m4a"

    output_file = stream.download(
        output_path=str(output_path),
        filename=filename,
        max_retries=3
    )

    print(f"Downloaded to: {output_file}")
    return output_file, yt

def extract_lyrics_from_captions(yt: YouTube):
    """Extract lyrics from YouTube captions if available"""
    try:
        captions = yt.captions

        if not captions:
            return None

        first_caption = next(iter(captions.values()))

        if first_caption:
            print(f"Found captions: {first_caption.name}")
            # get the caption text
            caption_text = first_caption.generate_srt_captions()

            # parse srt format to extract just the text
            lines = caption_text.split('\n')
            lyrics_lines = []

            for line in lines:
                line = line.strip()

                if line and not line.isdigit() and '-->' not in line:
                    lyrics_lines.append(line)

            lyrics = '\n'.join(lyrics_lines)

            if lyrics:
                print(f"Extracted {len(lyrics_lines)} lines of captions")
                return lyrics
            
    except Exception as e:
        print(f"Warning: Could not extract captions: {e}")

    return None

def get_thumbnail(yt: YouTube, image_filename: str):
    """Extract the image thumbnail from Youtube"""
    thumbnail_url = yt.thumbnail_url

    if not thumbnail_url:
        return None
    
    out = Path() / "data" / "album_art" / image_filename

    resp = requests.get(thumbnail_url, timeout=5)
    resp.raise_for_status()

    out.write_bytes(resp.content)
    print(f"Saved to {out.resolve()}")

    return out

def convert_m4ato_mp3(src, dst = None, quality: str = "0", remove_source=False):
    """Convert M4A file to MP3 using ffmpeg"""
    src_path = Path(src)

    if dst is None:
        dst = src_path.with_suffix('.mp3')

    dst_path = Path(dst)
    dst_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"\nConverting to MP3...")
    print(f"   Source: {str(src_path)}")
    print(f"   Destination: {str(dst_path)}")

    try:
        subprocess.run(
            [
                "ffmpeg",
                "-y",  # overwrite output file
                "-i", str(src_path),  # input file
                "-vn",  # no video
                "-c:a", "libmp3lame",
                "-q:a", quality,  # quality: 0 (best) to 9 (worst)
                str(dst_path)
            ],
            check=True,
            capture_output=True
        )

        print("M4A -> MP3 complete")

        if remove_source and src_path.exists():
            src_path.unlink()
            print(f"Removed source file: {src_path}")

        return str(dst_path)
    
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during conversion: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("❌ ffmpeg not found. Please install ffmpeg first.")
        sys.exit(1)

def edit_metadata(filepath, 
                  title=None, 
                  artists=None, 
                  album=None, 
                  year=None,
                  genre=None, 
                  lyrics=None,
                  album_art_path=None):
    """Edit metadata using mutagen"""
    file_path = Path(filepath)

    if not file_path.exists():
        print(f"❌ File not found: {filepath}")

    print(f"\n✏️  Editing metadata for: {file_path.name}")

    # handle multiple artists
    if artists:
        if isinstance(artists, str):
            # split by comma and strip whitespace
            artists = [a.strip() for a in artists.split()]
        elif not isinstance(artists, list):
            artists = [str(artists)]

    # read album art if provided
    album_art_data = None
    album_art_mime = None
    if album_art_path:
        art_path = Path(album_art_path)
        if art_path.exists():
            try:
                with open(art_path, 'rb') as img:
                    album_art_data = img.read()

                # determine MIME type from extension
                ext = art_path.suffix.lower()
                if ext in ['.jpg', '.jpeg']:
                    album_art_mime = 'image/jpeg'
                elif ext == '.png':
                    album_art_mime = 'image/png'
                else:
                    print(f"Unsupported image format: {ext}")
                    album_art_data = None

            except Exception as e:
                print(f"Error reading album art: {e}")

        else:
            print(f"Album art file not found: {album_art_path}")

    try:
        if file_path.suffix.lower() == '.mp3':
            # handle mp3 files
            try:
                audio = MP3(file_path, ID3=ID3)
            except:
                audio = MP3(filepath)
                audio.add_tags()

            if title:
                audio.tags.add(TIT2(encoding=3, text=title))
            if artists:
                audio.tags.add(TPE1(encoding=3, text=artists))
            if album:
                audio.tags.add(TALB(encoding=3, text=album))
            if year:
                audio.tags.add(TYER(encoding=3, text=str(year)))
            if genre:
                audio.tags.add(TCON(encoding=3, text=genre))
            if lyrics:
                audio.tags.add(USLT(encoding=3, lang='eng', desc='', text=lyrics))
            if album_art_data and album_art_mime:
                audio.tags.add(
                    APIC(
                        encoding=3,
                        mime=album_art_mime,
                        type=3,  # front cover
                        desc='Cover',
                        data=album_art_data
                    )
                )
            
            audio.save()

        elif file_path.suffix.lower() == '.m4a':
            # handle M4A files
            audio = MP4(filepath)

            if title:
                audio.tags['\xa9nam'] = title
            if artist:
                audio.tags['\xa9ART'] = artists
            if album:
                audio.tags['\xa9alb'] = album
            if year:
                audio.tags['\xa9day'] = str(year)
            if genre:
                audio.tags['\xa9gen'] = genre
            if lyrics:
                audio.tags['\xa9lyr'] = lyrics
            if album_art_data:
                if album_art_mime == 'image/png':
                    audio.tags['covr'] = [MP4Cover(album_art_data, imageformat=MP4Cover.FORMAT_PNG)]
                else:
                    audio.tags['covr'] = [MP4Cover(album_art_data, imageformat=MP4Cover.FORMAT_JPEG)]
            
            audio.save()

        else:
            print(f"Unsupported file format: {file_path.suffix}")
            return
        
        print("Metadata updated successfully")

        # Display updated metadata
        if any([title, artists, album, year, genre, lyrics, album_art_data]):
            print("\n📋 Updated metadata:")
            if title:
                print(f"   Title: {title}")
            if artists:
                print(f"   Artist: {artists}")
            if album:
                print(f"   Album: {album}")
            if year:
                print(f"   Year: {year}")
            if genre:
                print(f"   Genre: {genre}")
            if lyrics:
                lines_count = len(lyrics.split('\n'))
                print(f"   Lyrics: {lines_count} lines added")
            if album_art_data:
                size_kb = len(album_art_data) / 1024
                print(f"   Album Art: {size_kb:.1f} KB ({album_art_mime})")
    except Exception as e:
        print(f"Error editing metadata: {e}")

def main():
    parser = argparse.ArgumentParser(
        description="YouTube Music Downloader - Download, convert, and edit music metadata",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download only
  %(prog)s https://www.youtube.com/watch?v=VIDEO_ID
  
  # Download and convert to MP3
  %(prog)s https://www.youtube.com/watch?v=VIDEO_ID --convert
  
  # Download, convert, and edit metadata with custom album art
  %(prog)s https://www.youtube.com/watch?v=VIDEO_ID --convert \\
    --title "Song Title" --artist "Artist Name" --album "Album Name" \\
    --album-art "./covers/my_cover.jpg"
  
  # Use YouTube thumbnail as album art
  %(prog)s https://www.youtube.com/watch?v=VIDEO_ID --convert \\
    --use-thumbnail
  
  # Specify custom output directory and filename
  %(prog)s https://www.youtube.com/watch?v=VIDEO_ID --output ./music \\
    --filename "my_song.m4a"
        """
    )

    parser.add_argument('url', help='YouTube video URL')
    parser.add_argument('-o', '--output', default='./data/m4a', 
                        help='Output directory (default: ./data/m4a)')
    parser.add_argument('-f', '--filename', help='Output filename (optional)')

    # conversion options
    parser.add_argument('-c', '--convert', action='store_true',
                        help='Convert M4A to MP3')
    parser.add_argument('-q', '--quality', default='0', choices=['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'],
                        help='MP3 quality: 0 (best) to 9 (worst), default: 0')
    parser.add_argument('--keep-source', action='store_true',
                        help='keep M4A file after conversion (default: remove)')
    parser.add_argument('--mp3-output', help='Custom output path for MP3 file')

    # metadata options
    parser.add_argument('-t', '--title', help='Song title')
    parser.add_argument('-a', '--artist', help='Artist name')
    parser.add_argument('-A', '--album', help='Album name')
    parser.add_argument('-y', '--year', help='Release year')
    parser.add_argument('-g', '--genre', help='Music genre')
    parser.add_argument('--album-art', help='Path to album art image')
    parser.add_argument('--use-thumbnail', action='store_true', help='Use YT thumbnail as album art')
    parser.add_argument('--thumbnail-filename', default='album_cover.jpg',
                        help='Directory to save thumbnails (default: ./data/album_art)')
    
    args = parser.parse_args()

    # download audio
    try:
        downloaded_file, yt_obj = download_audio(args.url, args.output, args.filename)
    except Exception as e:
        print(f"Youtube Download failed: {e}")
        sys.exit(1)

    final_file = downloaded_file

    # convert if requested
    if args.convert:
        mp3_output = args.mp3_output
        if mp3_output is None and args.filename:
            mp3_output = Path() / "data" / "audio_files" / Path(args.filename).with_suffix('.mp3').name

        final_file = convert_m4ato_mp3(
            downloaded_file,
            dst=mp3_output,
            quality=args.quality,
            remove_source=not args.keep_source
        )

    # edit metadata if any metadata arguments are provided
    lyrics = extract_lyrics_from_captions(yt_obj)

    # handle album art
    album_art_path = None
    if args.album_art:
        album_art_path = args.album_art
    elif args.use_thumbnail:
        # download and use YT thumbnail
        album_art_path = get_thumbnail(yt_obj, image_filename=args.thumbnail_filename)

    if any([args.title, args.artist, args.album, args.year, args.genre, album_art_path]) or lyrics:
        # Use YouTube metadata as fallback if not provided
        title = args.title or yt_obj.title
        
        edit_metadata(
            final_file,
            title=title,
            artists=args.artist,
            album=args.album,
            year=args.year,
            genre=args.genre,
            lyrics=lyrics,
            album_art_path=album_art_path
        )
    
    print(f"\n🎉 All done! Final file: {final_file}")

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)
