import subprocess
import sys
import time
from pathlib import Path
import traceback

SCRIPTS_DIR = Path("/scripts")
TMP_DIR = Path("/tmp/video_processing")
LOG_FILE = TMP_DIR / "pipeline.log"
PYTHON = "python3"

MAX_RETRIES = 2
RETRY_DELAY = 2 


def log(message: str):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}"
    print(line)
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def run(script: str, outputs: list[Path], *args):
    script_path = SCRIPTS_DIR / script
    if not script_path.exists():
        raise FileNotFoundError(f"Script not found: {script_path}")

    cmd = [PYTHON, str(script_path), *map(str, args)]

    for attempt in range(1, MAX_RETRIES + 2):
        try:
            log(f"Running {script} (attempt {attempt})")
            subprocess.run(cmd, check=True)
            log(f"{script} finished successfully")
            return

        except Exception as e:
            log(f"{script} failed: {e}")
            log(traceback.format_exc())

            for file in outputs:
                if file.exists():
                    try:
                        file.unlink()
                        log(f"Deleted corrupted file: {file}")
                    except Exception as del_err:
                        log(f"Failed to delete {file}: {del_err}")

            if attempt > MAX_RETRIES:
                log(f"{script} failed after {MAX_RETRIES + 1} attempts")
                raise

            log(f"Retrying {script} after {RETRY_DELAY}s...")
            time.sleep(RETRY_DELAY)


if __name__ == "__main__":
    TMP_DIR.mkdir(parents=True, exist_ok=True)

    try:
        run(
            "get_voice.py",
            outputs=[TMP_DIR / "voice.wav"]
        )

        run(
            "subtitles.py",
            outputs=[TMP_DIR / "subtitles.srt"]
        )

        run(
            "translate_subtitles.py",
            outputs=[TMP_DIR / "subtitles_ru.srt"]
        )

        run(
            "sub_into_video.py",
            outputs=[TMP_DIR / "video_subtitled.mp4"]
        )

        log("Pipeline finished successfully")

    except Exception as fatal:
        log(f"Pipeline aborted: {fatal}")
        sys.exit(1)
