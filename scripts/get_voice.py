import subprocess
from pathlib import Path

video = Path("/tmp/video_processing/video.mp4")
voice = Path("/tmp/video_processing/voice.wav")

subprocess.run([
    "ffmpeg", "-y",
    "-i", str(video),
    str(voice)
], check=True)

print(voice)
