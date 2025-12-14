import subprocess
from pathlib import Path
import sys

video = Path("/tmp/video_processing/video.mp4")
subs = Path("/tmp/video_processing/subtitles_ru.srt")
out = Path("/tmp/video_processing/video_subtitled.mp4")

if not subs.exists():
    print("subtitles.srt NOT FOUND")
    sys.exit(1)

if subs.stat().st_size == 0:
    print("subtitles.srt is EMPTY")
    sys.exit(1)

cmd = [
    "ffmpeg",
    "-y",
    "-i", str(video),
    "-vf", f"subtitles={subs}",
    str(out)
]

print("Running:", " ".join(cmd))
subprocess.run(cmd, check=True)

print(out)