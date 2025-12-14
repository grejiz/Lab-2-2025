from pathlib import Path

dir_path = Path("/tmp/video_processing")

for item in dir_path.iterdir():
    if item.is_file():
        item.unlink()
