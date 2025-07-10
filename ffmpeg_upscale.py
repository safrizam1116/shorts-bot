import subprocess

def upscale_to_2k(input_path, output_path):
    command = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-vf", "scale=-1:1440",
        "-c:a", "copy",
        output_path
    ]
    subprocess.run(command, check=True)