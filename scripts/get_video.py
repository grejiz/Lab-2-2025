import subprocess
import sys
from pathlib import Path

url = sys.argv[1]
out = Path("/tmp/video_processing/video.mp4")

out.parent.mkdir(parents=True, exist_ok=True)

subprocess.run([
    "yt-dlp",
    "-f", "mp4",
    "-o", str(out),
    url
], check=True)

print(out)