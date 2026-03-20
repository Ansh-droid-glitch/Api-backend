import os
from moviepy.video.io.VideoFileClip import VideoFileClip
import re

def parse_time(time_str):
    """Convert 'mm:ss' string to total seconds (float)."""
    parts = time_str.strip().split(":")
    if len(parts) == 2:
        minutes, seconds = parts
        return int(minutes) * 60 + float(seconds)
    elif len(parts) == 3:
        hours, minutes, seconds = parts
        return int(hours) * 3600 + int(minutes) * 60 + float(seconds)
    else:
        raise ValueError(f"Unrecognized time format: '{time_str}'")

def parse_timestamp(ts_str: str):
    ts_str = ts_str.strip()
    pattern = r'^(\d+):(\d{2})-(\d+):(\d{2})$'
    match = re.match(pattern, ts_str)
    if not match:
        raise ValueError(f"Expected format 'mm:ss-mm:ss', got: '{ts_str}'")

    start_m, start_s, end_m, end_s = map(int, match.groups())
    start = start_m * 60 + start_s
    end   = end_m   * 60 + end_s
    return start, end

def cut_clips(video_path, timestamps):
    """
    Cut clips from a video using MoviePy.

    Args:
        video_path: Path to the source video file.
        timestamps: A list of strings like ["5:26-8:30", "12:00-15:45"]
                    OR a list of (start, end) tuples in seconds.

    Returns:
        List of output file paths.
    """
    os.makedirs("output", exist_ok=True)
    clips = []

    with VideoFileClip(video_path) as video:
        for i, ts in enumerate(timestamps):
            # Accept both "5:26-8:30" strings and (start, end) tuples
            if isinstance(ts, str):
                start, end = parse_timestamp(ts)
            else:
                start, end = ts

            output_path = f"output/clip_{i}.mp4"

            clip = video.subclipped(start, end)
            clip.write_videofile(
                output_path,
                codec="libx264",
                audio_codec="aac",
                logger=None       # suppress verbose MoviePy output
            )
            clip.close()

            clips.append(output_path)
            print(f"Saved: {output_path}  ({start}s → {end}s)")

    return clips


# --- Example usage ---
if __name__ == "__main__":
    cut_clips("my_video.mp4", [
        "5:26-8:30",
        "12:00-15:45",
        "1:02:10-1:05:00",   # hh:mm:ss also works
    ])