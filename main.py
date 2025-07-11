import os
import time
import json
import datetime
import pytz
from flask import Flask
from threading import Thread

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

# === TIMEZONE WIB ===
def get_wib_time():
    return datetime.datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(pytz.timezone("Asia/Jakarta"))

# === CEK APAKAH JAM GANJIL (WIB) ===
def is_ganjil_hour():
    return get_wib_time().hour % 2 == 1

# === CEK LOG ===
def current_log_key():
    return get_wib_time().strftime("%Y-%m-%d-%H")

def already_uploaded():
    if not os.path.exists(LOG_PATH):
        return False
    with open(LOG_PATH, "r") as f:
        data = json.load(f)
    return current_log_key() in data

def mark_uploaded():
    os.makedirs("logs", exist_ok=True)
    if not os.path.exists(LOG_PATH):
        with open(LOG_PATH, "w") as f:
            json.dump([], f)
    with open(LOG_PATH, "r+") as f:
        data = json.load(f)
        key = current_log_key()
        if key not in data:
            data.append(key)
        f.seek(0)
        json.dump(data, f, indent=2)
        f.truncate()

# === OFFSET CLIP ===
def get_offset():
    if not os.path.exists(LOG_PATH):
        return 0
    with open(LOG_PATH, "r") as f:
        data = json.load(f)
    return len(data)

# === PROSES UTAMA ===
def upload_task():
    now = get_wib_time().strftime("%Y-%m-%d %H:%M:%S")
    print(f"🚀 [{now}] Mulai upload Shorts...")

    try:
        os.makedirs("input", exist_ok=True)
        os.makedirs("output", exist_ok=True)
        os.makedirs("final", exist_ok=True)

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
        print("✅ Upload selesai.")
    except Exception as e:
        print(f"❌ Gagal upload: {e}")

# === WEB SERVER UNTUK RENDER ===
app = Flask(__name__)

@app.route("/")
def index():
    return "🟢 Bot Shorts aktif - Web Service mode (Render.com)"

def run_flask():
    app.run(host="0.0.0.0", port=3000)

# === MAIN ===
if __name__ == "__main__":
    # Jalankan Flask agar port 3000 terbuka (agar Render.com aktif)
    Thread(target=run_flask).start()
    time.sleep(3)

    now = get_wib_time()
    print(f"⏰ Sekarang {now.strftime('%H:%M')} WIB")

    if is_ganjil_hour() and not already_uploaded():
        upload_task()
    else:
        print("⏳ Bukan jam ganjil WIB atau sudah upload. Menunggu jam ganjil berikutnya...")

    # Keep-alive agar tidak mati
    while True:
        time.sleep(60)
