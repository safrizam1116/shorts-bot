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
CLIP_DURATION = 28  # detik

# === BUAT FOLDER OTOMATIS ===
for folder in ["input", "output", "final", "logs"]:
    os.makedirs(folder, exist_ok=True)

# === WAKTU WIB ===
def get_wib_time():
    return datetime.datetime.now(datetime.timezone.utc).astimezone(pytz.timezone("Asia/Jakarta"))

# === HITUNG OFFSET (urutan keberapa klip) ===
def get_offset():
    if not os.path.exists(LOG_PATH):
        return 0
    with open(LOG_PATH, "r") as f:
        try:
            data = json.load(f)
            return len(data)
        except:
            return 0

def mark_uploaded():
    key = get_wib_time().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_PATH, "r+") as f:
        try:
            data = json.load(f)
        except:
            data = []
        data.append(key)
        f.seek(0)
        json.dump(data, f, indent=2)
        f.truncate()

# === PROSES PAKSA UPLOAD SEKARANG ===
def upload_task():
    now = get_wib_time().strftime("%Y-%m-%d %H:%M:%S")
    print(f"🚀 [{now} WIB] Paksa upload Shorts...")

    try:
        print("📥 Download video dari Google Drive...")
        download_from_gdrive(VIDEO_ID, INPUT_PATH)

        offset = get_offset()
        start = offset * CLIP_DURATION
        print(f"✂️ Potong video mulai detik ke-{start}")
        cut_video(INPUT_PATH, CLIP_PATH, start_time=start, duration=CLIP_DURATION)

        print("🔧 Upscaling ke 2K...")
        upscale_to_2k(CLIP_PATH, UPSCALED_PATH)

        print("📤 Upload ke YouTube...")
        upload_video(UPSCALED_PATH, title=f"🔥 Shorts {get_wib_time().strftime('%H:%M')}", description="#shorts #viral")

        mark_uploaded()
        print("✅ Upload selesai dan dicatat di log.")

    except Exception as e:
        print(f"❌ Gagal upload: {e}")

# === SERVER RENDER (agar tetap aktif) ===
app = Flask(__name__)
@app.route("/")
def index():
    return "🟢 Bot aktif — Paksa Upload Sekarang"

# === MAIN ===
if __name__ == "__main__":
    from waitress import serve
    upload_task()
    serve(app, host="0.0.0.0", port=3000)
