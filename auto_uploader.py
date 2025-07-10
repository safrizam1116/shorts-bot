from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os
import pickle

def upload_video(path, title, description):
    creds = None
    if os.path.exists("/etc/secrets/auth_token.pickle"):
        with open("/etc/secrets/auth_token.pickle", "rb") as token:
            creds = pickle.load(token)
    else:
        raise Exception("❌ auth_token.pickle not found")

    youtube = build("youtube", "v3", credentials=creds)
    request_body = {
        "snippet": {
            "categoryId": "22",
            "title": title,
            "description": description,
            "tags": ["shorts", "viral"]
        },
        "status": {"privacyStatus": "public"}
    }

    media = MediaFileUpload(path, mimetype="video/*", resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=request_body, media_body=media)

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Uploading... {int(status.progress() * 100)}%")
    print(f"✅ Uploaded! Video ID: {response['id']}")