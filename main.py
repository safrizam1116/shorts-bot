import time
import datetime
import os
import json
import pytz
import requests
from threading import Thread
from flask import Flask
from downloader import download_from_gdrive
from cutter import cut_video
from auto_uploader import upload_video

# KONFIGURASI
VIDEO_ID = "1i8iT8IR5nzVNcyLSaue1l5WWNkve0xiR"
INPUT_PATH = "input/video.mp4"
OUTPUT_PATH = "final/short.mp4"
UPLOAD_LOG = "logs/uploaded.json"
CLIP_DURATION = 27
STATUS_URL = "https://shorts-control.onrender.com/status"

# FUNGSI WAKTU
def get_current_wib_time():
    utc_now = datetime.datetime.utcnow()
    wib = utc_now.replace(tzinfo=pytz.utc).astimezone(pytz.timezone("Asia/Jakarta"))
    return wib

def is_odd_hour():
    now = get_current_wib_time()
    return now.hour % 2 == 1

def already_uploaded():
    if not os.path.exists(UPLOAD_LOG):
        return False
    with open(UPLOAD_LOG) as f:
        log = json.load(f)
    jam = get_current_wib_time().strftime("%Y-%m-%d-%H")
    return jam in log

def save_uploaded():
    jam = get_current_wib_time().strftime("%Y-%m-%d-%H")
    os.makedirs("logs", exist_ok=True)
    if not os.path.exists(UPLOAD_LOG):
        json.dump([], open(UPLOAD_LOG, "w"))
    with open(UPLOAD_LOG, "r+") as f:
        data = json.load(f)
        data.append(jam)
        f.seek(0)
        json.dump(data, f)
        f.truncate()

def get_offset():
    offset_file = "logs/offset.json"
    if not os.path.exists(offset_file):
        return 0
    with open(offset_file) as f:
        return json.load(f).get("offset", 0)

def save_offset(offset):
    with open("logs/offset.json", "w") as f:
        json.dump({"offset": offset}, f)

# FAKE SERVER UNTUK RENDER
app = Flask(__name__)
@app.route("/")
def home():
    return "🟢 Bot Shorts is Running"

def run_flask():
    app.run(host="0.0.0.0", port=3000)

# TUGAS UPLOAD
def upload_task():
    try:
        print("⏳ Cek status bot dan jam...")
        res = requests.get(STATUS_URL, timeout=10)
        if res.status_code != 200 or res.json().get("status") != "ON":
            print("🛑 Status = OFF → Bot tidak jalan.")
            return

        if not is_odd_hour():
            print("🕑 Bukan jam ganjil WIB.")
            return

        if already_uploaded():
            print("✅ Sudah upload jam ini.")
            return

        os.makedirs("input", exist_ok=True)
        download_from_gdrive(VIDEO_ID, INPUT_PATH)

        offset = get_offset()
        start = offset * CLIP_DURATION
        cut_video(INPUT_PATH, OUTPUT_PATH, start_time=start, duration=CLIP_DURATION)
        upload_video(OUTPUT_PATH, title="🔥 Shorts Otomatis", description="#shorts #jadwal")

        save_uploaded()
        save_offset(offset + 1)

        print("✅ Upload selesai.")

    except Exception as e:
        print(f"❌ Error: {e}")

# MAIN
if __name__ == "__main__":
    Thread(target=run_flask).start()
    time.sleep(3)
    upload_task()
    while True:
        time.sleep(300)
