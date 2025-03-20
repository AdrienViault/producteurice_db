import os
import json
import subprocess
import pytest
from PIL import Image

# -------------------------
# JSON Seed Files Verification
# -------------------------
def test_seed_json_files():
    seeds_root = "table_seeds"
    for root, _, files in os.walk(seeds_root):
        for file in files:
            if file.endswith(".json"):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    try:
                        json.load(f)
                    except json.JSONDecodeError as e:
                        pytest.fail(f"JSON file {file_path} is invalid: {e}")

# -------------------------
# Image Files Verification
# -------------------------
def test_media_photos_readable():
    # Allowed image extensions.
    photo_extensions = (".png", ".jpg", ".jpeg", ".webp")
    media_root = "media"
    for root, _, files in os.walk(media_root):
        for file in files:
            if file.lower().endswith(photo_extensions):
                file_path = os.path.join(root, file)
                try:
                    with Image.open(file_path) as img:
                        img.verify()  # Verifies image integrity.
                except Exception as e:
                    pytest.fail(f"Image file {file_path} is not readable: {e}")

# -------------------------
# Video Files Verification (H264 MP4)
# -------------------------
def get_video_codec(file_path):
    """
    Uses ffprobe to return the codec of the first video stream in the file.
    """
    command = [
        "ffprobe", "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=codec_name",
        "-of", "default=nw=1:nk=1",
        file_path
    ]
    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            check=True,
        )
        codec = result.stdout.strip()
        return codec
    except subprocess.CalledProcessError as e:
        pytest.fail(f"ffprobe error for {file_path}: {e.stderr}")

def test_media_videos_readable():
    # Allowed video extensions (mp4)
    video_extensions = (".mp4",)
    media_root = "media"
    for root, _, files in os.walk(media_root):
        for file in files:
            if file.lower().endswith(video_extensions):
                file_path = os.path.join(root, file)
                # Check file is non-empty.
                assert os.path.getsize(file_path) > 0, f"Video file {file_path} is empty."
                # Check the codec is H264.
                codec = get_video_codec(file_path)
                assert codec.lower() == "h264", f"Video file {file_path} is not encoded in H264 (found {codec})."
