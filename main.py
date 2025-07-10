import time
import datetime
import os
import json
import pytz
from threading import Thread
from flask import Flask
from downloader import download_from_gdrive
from cutter import cut_video
from auto_uploader import upload_video
from ffmpeg_upscale import upscale_to_2k

VIDEO_ID = "1QskinABo707mG4dxdzv8Mna8pGS-WBGj"
INPUT_PATH = "input/video.mp4"
CUT_PATH = "output/short.mp4"
UPSCALED_PATH = "upscale/short_upscaled.mp4"
UPLOAD_LOG = "logs/uploaded.json"
CLIP_DURATION = 28

def get_wib_time():
    return datetime.datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(pytz.timezone("Asia/Jakarta"))

def is_odd_hour():
    now = get_wib_time()
    return now.hour % 2 == 1

def current_key():
    return get_wib_time().strftime("%Y-%m-%d-%H")

def has_uploaded():
    if not os.path.exists(UPLOAD_LOG): return False
    with open(UPLOAD_LOG) as f:
        return current_key() in json.load(f)

def save_uploaded():
    os.makedirs("logs", exist_ok=True)
    if not os.path.exists(UPLOAD_LOG):
        with open(UPLOAD_LOG, "w") as f: json.dump([], f)
    with open(UPLOAD_LOG, "r+") as f:
        log = json.load(f)
        key = current_key()
        if key not in log:
            log.append(key)
            f.seek(0)
            json.dump(log, f)
            f.truncate()

def get_offset():
    if not os.path.exists(UPLOAD_LOG): return 0
    with open(UPLOAD_LOG) as f:
        log = json.load(f)
        return len(log)

def upload_task():
    try:
        os.makedirs("input", exist_ok=True)
        os.makedirs("output", exist_ok=True)
        os.makedirs("upscale", exist_ok=True)

        print("📥 Downloading...")
        download_from_gdrive(VIDEO_ID, INPUT_PATH)

        offset = get_offset()
        start_time = offset * CLIP_DURATION

        print("✂️ Cutting...")
        cut_video(INPUT_PATH, CUT_PATH, start_time=start_time, duration=CLIP_DURATION)

        print("🔧 Upscaling...")
        upscale_to_2k(CUT_PATH, UPSCALED_PATH)

        print("📤 Uploading...")
        upload_video(UPSCALED_PATH, title=f"🔥 Shorts {get_wib_time().strftime('%H:%M')}", description="#shorts #viral")

        save_uploaded()
        print("✅ Done.")

    except Exception as e:
        print(f"❌ Error: {e}")

app = Flask(__name__)
@app.route("/")
def home(): return "🟢 Shorts Bot Active"

def run_server():
    app.run(host="0.0.0.0", port=3000)

if __name__ == "__main__":
    Thread(target=run_server).start()
    time.sleep(3)

    if is_odd_hour() and not has_uploaded():
        upload_task()
    else:
        print(f"⏳ Bukan jam ganjil atau sudah upload. Sekarang: {get_wib_time().strftime('%H:%M')}")
    while True:
        time.sleep(30)