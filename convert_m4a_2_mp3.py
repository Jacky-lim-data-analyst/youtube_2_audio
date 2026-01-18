import subprocess

def m4a_to_mp3(src, dst, quality="0"):
    subprocess.run(
        [
            "ffmpeg",
            "-y",    # overwrite output file
            "-i", src,    # input file
            "-vn",    # no video
            "-c:a", "libmp3lame",
            "-q:a", quality,
            dst   
        ],
        check=True
    )

if __name__ == "__main__":
    source_file_path = "./audio_files/eric_chou_duo_yuan_dou_yao_zai_yi_qi.m4a"
    remove_source = True
    m4a_to_mp3(
        src=source_file_path,
        dst="./mp3_files/eric_chou_duo_yuan_dou_yao_zai_yi_qi.mp3"
    )

    if remove_source:
        import os
        if os.path.exists(source_file_path):
            os.remove(source_file_path)
            print(f"Removed {source_file_path}")
