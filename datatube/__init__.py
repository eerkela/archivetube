from pathlib import Path

DATATUBE_VERSION_NUMBER = 0.1
ROOT_DIR = Path(__file__).resolve().parent.parent
VIDEO_DIR = Path(ROOT_DIR, "videos")
AVAILABLE_SOURCES = ("local", "pytube", "sql")


def is_channel_id(id_str: str) -> bool:
    return len(id_str) == 24 and id_str.startswith("UC")


def is_readable(path: Path) -> bool:
    return path.is_dir() and len(path.glob("info.json")) > 0


def is_video_id(id_str: str) -> bool:
    return len(id_str) == 11
