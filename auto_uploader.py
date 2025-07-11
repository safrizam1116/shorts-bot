import os
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from dotenv import load_dotenv

load_dotenv()

def get_authenticated_service():
    creds = Credentials.from_authorized_user_file("/etc/secrets/auth_token.json", scopes=["https://www.googleapis.com/auth/youtube.upload"])
    return build("youtube", "v3", credentials=creds)

def upload_video(file_path, title, description):
    youtube = get_authenticated_service()
    media = MediaFileUpload(file_path, chunksize=-1, resumable=True, mimetype='video/*')
    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description,
                "tags": ["shorts", "viral"],
                "categoryId": "22"
            },
            "status": {
                "privacyStatus": "public"
            }
        },
        media_body=media
    )
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"📤 Uploading: {int(status.progress() * 100)}%")
    print(f"✅ Upload selesai → https://youtu.be/{response['id']}")