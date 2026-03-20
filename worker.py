from utils.ai import get_highlights
from utils.clipper import cut_clips

def process_video(video_path: str):
    timestamps = get_highlights(video_path)  # now returns a list
    clips = cut_clips(video_path, timestamps)
    return clips