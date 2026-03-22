import os
import time
import subprocess
import requests
from dotenv import load_dotenv
from utils.send_text import query_text as send_text

load_dotenv()

ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
BASE_URL = "https://api.assemblyai.com/v2"
HEADERS = {"authorization": ASSEMBLYAI_API_KEY}


def upload_audio(file_path: str) -> str:
    with open(file_path, "rb") as f:
        response = requests.post(f"{BASE_URL}/upload", headers=HEADERS, data=f)
    response.raise_for_status()
    return response.json()["upload_url"]


def transcribe(audio_url: str) -> str:
    response = requests.post(
        f"{BASE_URL}/transcript",
        headers=HEADERS,
        json={"audio_url": audio_url}
    )
    response.raise_for_status()
    transcript_id = response.json()["id"]

    poll_url = f"{BASE_URL}/transcript/{transcript_id}"
    while True:
        result = requests.get(poll_url, headers=HEADERS).json()
        if result["status"] == "completed":
            return result["text"]
        elif result["status"] == "error":
            raise RuntimeError(f"Transcription error: {result.get('error')}")
        time.sleep(3)


def get_highlights(video_path: str):
    audio_path = "audio.mp3"

    # Step 1: Extract audio from video
    command = [
        "ffmpeg", "-i", video_path,
        "-q:a", "0", "-map", "a",
        audio_path, "-y"
    ]
    try:
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"Audio extracted to {audio_path}")
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg error: {e.stderr.decode()}")
        return ""
    except FileNotFoundError:
        print("Error: ffmpeg not found. Make sure FFmpeg is installed and added to PATH.")
        return ""

    # Step 2: Upload and transcribe
    try:
        print("Uploading audio to AssemblyAI...")
        audio_url = upload_audio(audio_path)
        print("Transcribing...")
        result = transcribe(audio_url)
        print(f"Transcription complete. Total characters: {len(result)}")
    except Exception as e:
        print(f"Transcription failed: {e}")
        return []
    finally:
        if os.path.exists(audio_path):
            os.remove(audio_path)

    # Step 3: Get highlights
    timestamps = send_text(result)
    print(f"Timestamps received: {timestamps}")
    return timestamps