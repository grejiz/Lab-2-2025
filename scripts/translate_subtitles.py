import os
import requests
from pathlib import Path

SRC = Path("/tmp/video_processing/subtitles.srt")
DST = Path("/tmp/video_processing/subtitles_ru.srt")

OLLAMA_URL = "http://ollama:11434/api/generate"
MODEL = "qwen2.5:3b-instruct"

PROMPT_TEMPLATE = os.getenv("SUBTITLE_TRANSLATION_PROMPT")
if not PROMPT_TEMPLATE:
    raise RuntimeError("SUBTITLE_TRANSLATION_PROMPT is not set")

def translate(text: str) -> str:
    prompt = f"""{PROMPT_TEMPLATE}

{text}
"""

    r = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.3
            }
        },
        timeout=300
    )
    r.raise_for_status()
    return r.json()["response"].strip()

blocks = SRC.read_text(encoding="utf-8").split("\n\n")
out = []

for block in blocks:
    lines = block.splitlines()

    if len(lines) < 3:
        out.append(block)
        continue

    number = lines[0]
    timing = lines[1]
    text = "\n".join(lines[2:])

    translated = translate(text)

    out.append("\n".join([number, timing, translated]))

DST.write_text("\n\n".join(out), encoding="utf-8")
print(f"Saved: {DST}")
