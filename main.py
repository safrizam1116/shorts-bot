import os
import time
import json
import pytz
import datetime
from threading import Thread
from flask import Flask
from downloader import download_from_gdrive
from cutter import cut_video
from ffmpeg_upscale import upscale_to_2k
from auto_uploader import upload_video

# ==== KONFIGURASI ====
VIDEO_ID = "1QskinABo707mG4dxdzv8Mna8pGS-WBGj"
INPUT_PATH = "input/video.mp4"
CLIP_PATH = "output/short.mp4"
UPSCALED_PATH = "upscale/short_upscaled.mp4"
LOG_PATH = "logs/uploaded.json"
CLIP_DURATION = 28

# ==== WIB TIME ====
def now_wib():
    utc_now = datetime.datetime.utcnow()
    return utc_now.replace(tzinfo=pytz.utc).astimezone(pytz.timezone("Asia/Jakarta"))

def is_ganjil_hour():
    now = now_wib()
    return now.hour % 2 == 1

def has_uploaded_this_hour():
    if not os.path.exists(LOG_PATH):
        return False
    with open(LOG_PATH, "r") as f:
        data = json.load(f)
    current_hour = now_wib().strftime("%Y-%m-%d-%H")
    return current_hour in data

def log_upload():
    os.makedirs("logs", exist_ok=True)
    current_hour = now_wib().strftime("%Y-%m-%d-%H")
    if not os.path.exists(LOG_PATH):
        with open(LOG_PATH, "w") as f:
            json.dump([], f)
    with open(LOG_PATH, "r+") as f:
        data = json.load(f)
        if current_hour not in data:
            data.append(current_hour)
        f.seek(0)
        json.dump(data, f)
        f.truncate()

def get_offset():
    if not os.path.exists(LOG_PATH):
        return 0
    with open(LOG_PATH, "r") as f:
        data = json.load(f)
        return data.count("\n") if isinstance(data, str) else len(data)

# ==== MAIN TASK ====
def run_bot():
    print(f"🕒 {now_wib().strftime('%Y-%m-%d %H:%M:%S')} WIB | Checking upload window...")

    if is_ganjil_hour() and not has_uploaded_this_hour():
        try:
            os.makedirs("input", exist_ok=True)
            os.makedirs("output", exist_ok=True)
            os.makedirs("upscale", exist_ok=True)

            download_from_gdrive(VIDEO_ID, INPUT_PATH)

            offset = get_offset()
            start_time = offset * CLIP_DURATION
            cut_video(INPUT_PATH, CLIP_PATH, start_time=start_time, duration=CLIP_DURATION)

            upscale_to_2k(CLIP_PATH, UPSCALED_PATH)

            upload_video(UPSCALED_PATH, title="🔥 Shorts Jedag Jedug", description="#shorts #viral")
            log_upload()

            print("✅ Upload completed.")

        except Exception as e:
            print(f"❌ Error during process: {e}")
    else:
        print("⏳ Not a ganjil hour or already uploaded this hour.")

# ==== FAKE SERVER FOR RENDER ====
app = Flask(__name__)

@app.route('/')
def index():
    return f"✅ Bot aktif: {now_wib().strftime('%Y-%m-%d %H:%M:%S')} WIB"

def keep_alive():
    Thread(target=lambda: app.run(host="0.0.0.0", port=3000)).start()

# ==== MAIN LOOP ====
if __name__ == "__main__":
    keep_alive()
    while True:
        run_bot()
        time.sleep(60 * 60)  # Cek per 1 jam
