import sys
import subprocess
from pathlib import Path
import math
import requests

VOICE = Path("/tmp/video_processing/voice.wav")
SRT = Path("/tmp/video_processing/subtitles.srt")
WHISPER_API = "http://auto-subtitle-api:9000"

def get_voice_duration(voice):
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        voice
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(result.stdout.strip())

def seconds_to_srt_time(seconds):
    ms = int((seconds - int(seconds)) * 1000)
    s = int(seconds)
    h = s // 3600
    m = (s % 3600) // 60
    s = s % 60
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

def generate_srt(text, voice_duration, output_path):
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    if not lines:
        raise ValueError("Empty transcription")

    segment_duration = voice_duration / len(lines)

    srt = []
    for i, line in enumerate(lines):
        start = i * segment_duration
        end = start + segment_duration
        srt.append(
            f"{i+1}\n"
            f"{seconds_to_srt_time(start)} --> {seconds_to_srt_time(end)}\n"
            f"{line}\n"
        )

    output_path.write_text("\n".join(srt), encoding="utf-8")

if __name__ == "__main__":
    voice_path = VOICE
    output_srt = SRT
    api_url = WHISPER_API

    with open(voice_path, "rb") as f:
        r = requests.post(
            f"{api_url}/asr",
            files={"audio_file": f},
            data={"task": "transcribe", "language": "en"},
            timeout=300
        )

    if r.status_code != 200:
        raise RuntimeError(f"Whisper API error: {r.text}")

    text = r.text.strip()
    duration = get_voice_duration(str(voice_path))
    generate_srt(text, duration, output_srt)

    print(f"SRT generated: {output_srt}")
