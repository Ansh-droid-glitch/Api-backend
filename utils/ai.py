from dotenv import load_dotenv
import os
import speech_recognition as sr
from pydub import AudioSegment
from utils.send_text import query_text as send_text
import subprocess

def get_highlights(video_path: str):
    src = "audio.mp3"
    dst = "audio.wav"
    r = sr.Recognizer()

    # Step 1: Extract audio from video using FFmpeg
    command = [
        'ffmpeg',
        '-i', video_path,
        '-q:a', '0',
        '-map', 'a',
        src,
        '-y'  # Overwrite output file if it exists
    ]
    try:
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"Audio successfully extracted and saved to {src}")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e.stderr.decode()}")
        return ""
    except FileNotFoundError:
        print("Error: ffmpeg not found. Make sure FFmpeg is installed and added to PATH.")
        return ""

    # Step 2: Convert MP3 to WAV
    try:
        sound = AudioSegment.from_mp3(src)
        sound.export(dst, format="wav")
        print(f"Successfully converted {src} to {dst}")
    except Exception as e:
        print(f"Error during conversion: {e}")
        return ""

    # Step 3: Split audio into 30-second chunks
    chunk_length_ms = 30 * 1000
    chunks = [sound[i:i + chunk_length_ms] for i in range(0, len(sound), chunk_length_ms)]
    print(f"Audio split into {len(chunks)} chunk(s) of 30 seconds each.")

    # Step 4: Transcribe each chunk
    full_text = []
    for i, chunk in enumerate(chunks):
        chunk_path = f"chunk_{i}.wav"
        chunk.export(chunk_path, format="wav")

        with sr.AudioFile(chunk_path) as source:
            print(f"Reading chunk {i + 1}/{len(chunks)}...")
            audio = r.record(source)

        try:
            print(f"Transcribing chunk {i + 1}/{len(chunks)}...")
            text = r.recognize_google(audio)
            full_text.append(text)
            print(f"Chunk {i + 1} transcribed: {text[:60]}...")
        except sr.UnknownValueError:
            print(f"Chunk {i + 1}: Could not understand audio, skipping.")
        except sr.RequestError as e:
            print(f"Chunk {i + 1}: API request failed — {e}")
        finally:
            # Clean up chunk file
            if os.path.exists(chunk_path):
                os.remove(chunk_path)

    # Step 5: Combine and return result
    result = " ".join(full_text)

    if result:
        print(f"\nTranscription complete. Total characters: {len(result)}")
        timestamps = send_text(result)
        print(f"Timestamps received: {timestamps}")
        return timestamps
    else:
        print("Transcription failed or produced no output.")
        return []
        exit()