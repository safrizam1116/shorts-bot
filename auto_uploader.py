import os
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from oauth2client.file import Storage
from oauth2client.tools import run_flow
from oauth2client.client import flow_from_clientsecrets
from dotenv import load_dotenv

load_dotenv()

CLIENT_SECRET = os.getenv("CLIENT_SECRET", "/etc/secrets/credentials.json")
TOKEN_PATH = os.getenv("TOKEN_PATH", "/etc/secrets/auth_token.json")

def get_authenticated_service():
    storage = Storage(TOKEN_PATH)
    credentials = storage.get()

    if not credentials or credentials.invalid:
        flow = flow_from_clientsecrets(CLIENT_SECRET, scope="https://www.googleapis.com/auth/youtube.upload")
        credentials = run_flow(flow, storage)

    return build('youtube', 'v3', credentials=credentials)

def upload_video(file_path, title="My Shorts", description="#shorts"):
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
            print(f"Uploading: {int(status.progress() * 100)}%")
    print(f"✅ Upload selesai → https://youtube.com/watch?v={response['id']}")
