# utils/clipper.py
import os
import re
from moviepy.video.io.VideoFileClip import VideoFileClip


def parse_timestamp(ts_str: str):
    ts_str = ts_str.strip()
    match = re.match(r'^(\d+):(\d{2})-(\d+):(\d{2})$', ts_str)
    if not match:
        raise ValueError(f"Expected format 'mm:ss-mm:ss', got: '{ts_str}'")
    start_m, start_s, end_m, end_s = map(int, match.groups())
    return start_m * 60 + start_s, end_m * 60 + end_s


def cut_clips(video_path: str, timestamps: list) -> list[str]:
    os.makedirs("output", exist_ok=True)
    clips = []

    with VideoFileClip(video_path) as video:
        for i, ts in enumerate(timestamps):
            start, end = parse_timestamp(ts) if isinstance(ts, str) else ts

            # Clamp end to video duration to avoid out-of-bounds errors
            end = min(end, video.duration)

            if start >= end:
                print(f"Skipping clip {i}: start ({start}s) >= end ({end}s)")
                continue

            output_path = f"output/clip_{i}.mp4"

            try:
                clip = video.subclipped(start, end)
                clip.write_videofile(
                    output_path,
                    codec="libx264",
                    audio_codec="aac",
                    preset="ultrafast",
                    logger=None,        # suppress verbose moviepy logs
                )
                clip.close()
                clips.append(output_path)
                print(f"Saved: {output_path}  ({start}s → {end}s)")
            except Exception as e:
                print(f"Failed on clip {i}: {e}")

    return clips