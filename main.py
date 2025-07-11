import os
import time
import json
import datetime
import pytz
from flask import Flask
from downloader import download_from_gdrive
from cutter import cut_video
from ffmpeg_upscale import upscale_to_2k
from auto_uploader import upload_video

# === KONFIGURASI ===
VIDEO_ID = "1QskinABo707mG4dxdzv8Mna8pGS-WBGj"
INPUT_PATH = "input/video.mp4"
CLIP_PATH = "output/short.mp4"
UPSCALED_PATH = "final/short_upscaled.mp4"
LOG_PATH = "logs/uploaded.json"
CLIP_DURATION = 28

# === TIMEZONE WIB ===
def get_wib_time():
    return datetime.datetime.now(datetime.timezone.utc).astimezone(pytz.timezone("Asia/Jakarta"))

# === LOGIC CLIP OFFSET ===
def get_offset():
    if not os.path.exists(LOG_PATH):
        return 0
    with open(LOG_PATH, "r") as f:
        data = json.load(f)
    return len(data)

def mark_uploaded():
    if not os.path.exists(LOG_PATH):
        with open(LOG_PATH, "w") as f:
            json.dump([], f)
    with open(LOG_PATH, "r+") as f:
        data = json.load(f)
        key = get_wib_time().strftime("%Y-%m-%d-%H")
        if key not in data:
            data.append(key)
        f.seek(0)
        json.dump(data, f, indent=2)
        f.truncate()

# === PROSES PAKSA UPLOAD ===
def upload_task():
    now = get_wib_time().strftime("%Y-%m-%d %H:%M:%S")
    print(f"🚀 [{now} WIB] Mulai upload Shorts...")

    try:
        print("📥 Download video...")
        download_from_gdrive(VIDEO_ID, INPUT_PATH)
        print("✅ Selesai download")

        offset = get_offset()
        start = offset * CLIP_DURATION

        print(f"✂️ Potong video mulai detik ke-{start}")
        cut_video(INPUT_PATH, CLIP_PATH, start_time=start, duration=CLIP_DURATION)
        print("✅ Selesai potong")

        print("🔧 Upscaling ke 2K...")
        upscale_to_2k(CLIP_PATH, UPSCALED_PATH)
        print("✅ Selesai upscale")

        print("📤 Upload ke YouTube...")
        upload_video(UPSCALED_PATH, title=f"🔥 Shorts {get_wib_time().strftime('%H:%M')}", description="#shorts #viral")
        print("✅ Selesai upload")

        mark_uploaded()

    except Exception as e:
        print(f"❌ Gagal: {e}")

# === SERVER (AGAR RENDER HIDUP) ===
app = Flask(__name__)
@app.route("/")
def index():
    return "🟢 Bot aktif — paksa upload"

if __name__ == "__main__":
    print("🔧 Test: Coba upload langsung")
    upload_task()


    from waitress import serve
    serve(app, host="0.0.0.0", port=3000)
