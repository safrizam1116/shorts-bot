import subprocess

def cut_video(input_path, output_path, start_time=0, duration=28):
    command = [
        "ffmpeg", "-y",
        "-ss", str(start_time),
        "-i", input_path,
        "-t", str(duration),
        "-vf", "scale=720:1280",
        "-c:a", "copy",
        output_path
    ]
    subprocess.run(command, check=True)