from fastapi import FastAPI, UploadFile
from worker import process_video
from pydantic import BaseModel
import subprocess
import os

app = FastAPI()

@app.post("/process")
async def process(file: UploadFile):
    path = f"temp_{file.filename}"

    with open(path, "wb") as f:
        f.write(await file.read())

    result = process_video(path)

    return {"clips": result}



class YoutubeRequest(BaseModel):
    url: str

@app.post("/process_youtube")
async def process_youtube(body: YoutubeRequest):
    output_path = "temp_youtube.mp4"

    # Download video using yt-dlp
    command = [
        "yt-dlp",
        "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
        "-o", output_path,
        body.url
    ]

    try:
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"Downloaded video to {output_path}")
    except subprocess.CalledProcessError as e:
        return {"error": f"yt-dlp failed: {e.stderr.decode()}"}
    except FileNotFoundError:
        return {"error": "yt-dlp not found. Install it with: pip install yt-dlp"}

    result = process_video(output_path)

    # Clean up downloaded video
    if os.path.exists(output_path):
        os.remove(output_path)

    return {"clips": result}