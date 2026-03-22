import os
import time
import requests
from tqdm import tqdm

# Set your AssemblyAI API key
api_key = 'YOUR_ASSEMBLYAI_API_KEY'

# Folder containing audio files
audio_folder = 'audio_files'
srt_folder = 'srt_files'

# Ensure the output folder exists
os.makedirs(srt_folder, exist_ok=True)

BASE_URL = "https://api.assemblyai.com/v2"
HEADERS = {"authorization": api_key}


def upload_audio(file_path):
    """Upload a local audio file to AssemblyAI and return the upload URL."""
    upload_url = f"{BASE_URL}/upload"
    with open(file_path, "rb") as f:
        response = requests.post(upload_url, headers=HEADERS, data=f)
    if response.status_code != 200:
        raise Exception(f"Upload failed: {response.status_code} {response.text}")
    return response.json()["upload_url"]


def request_transcription(audio_url):
    """Submit a transcription job and return the transcript ID."""
    response = requests.post(
        f"{BASE_URL}/transcript",
        headers=HEADERS,
        json={"audio_url": audio_url}
    )
    if response.status_code != 200:
        raise Exception(f"Transcription request failed: {response.status_code} {response.text}")
    return response.json()["id"]


def poll_transcription(transcript_id):
    """Poll until the transcription is complete, then return the status."""
    poll_url = f"{BASE_URL}/transcript/{transcript_id}"
    while True:
        response = requests.get(poll_url, headers=HEADERS)
        result = response.json()
        status = result["status"]
        if status == "completed":
            return
        elif status == "error":
            raise Exception(f"Transcription error: {result.get('error')}")
        time.sleep(3)


def get_srt(transcript_id):
    """Fetch the transcript in SRT format."""
    response = requests.get(
        f"{BASE_URL}/transcript/{transcript_id}/srt",
        headers=HEADERS
    )
    if response.status_code != 200:
        raise Exception(f"SRT fetch failed: {response.status_code} {response.text}")
    return response.text


def transcribe_audio(file_path):
    audio_url = upload_audio(file_path)
    transcript_id = request_transcription(audio_url)
    poll_transcription(transcript_id)
    return get_srt(transcript_id)


def save_srt_file(srt_content, output_path):
    with open(output_path, 'w') as f:
        f.write(srt_content)


def main(file_path:str):
    audio_files = [file_path] # change filetype as needed

    for audio_file in tqdm(audio_files, desc="Processing audio files"):
        audio_path = os.path.join(audio_folder, audio_file)
        try:
            srt_content = transcribe_audio(audio_path)
            srt_file_name = os.path.splitext(audio_file)[0] + '.srt'
            srt_path = os.path.join(srt_folder, srt_file_name)
            save_srt_file(srt_content, "srt.srt")
        except Exception as e:
            print(f"Error processing {audio_file}: {e}")


if __name__ == "__main__":
    main("sample.mp3")