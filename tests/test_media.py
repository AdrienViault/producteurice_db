import os
import re

MEDIA_ROOT = "media"

# Regex patterns for each media category.
animal_photo_pattern = re.compile(
    r'^animal_(\d+)_photo_?(\d+)\.(png|jpg|jpeg|webp)$', re.IGNORECASE
)
crop_photo_pattern = re.compile(
    r'^crop_(\d+)_photo_?(\d+)\.(png|jpg|jpeg|webp)$', re.IGNORECASE
)
farm_documentary_pattern = re.compile(
    r'^farm_(\d+)_documentary_?(\d+)\.mp4$', re.IGNORECASE
)
farm_herovideo_pattern = re.compile(
    r'^farm_(\d+)_herovideo_?(\d+)\.mp4$', re.IGNORECASE
)
farm_photo_pattern = re.compile(
    r'^farm_(\d+)_photo_?(\d+)\.jpg$', re.IGNORECASE
)
farmer_photo_pattern = re.compile(
    r'^farmer_(\d+)_photo_?(\d+)\.jpg$', re.IGNORECASE
)
icons_pattern = re.compile(
    r'^[a-zA-Z0-9_]+\.svg$', re.IGNORECASE
)
product_photo_pattern = re.compile(
    r'^product_(\d+)_photo_?(\d+)\.(png|jpg|jpeg|webp)$', re.IGNORECASE
)

def test_animal_media():
    animal_root = os.path.join(MEDIA_ROOT, "animal")
    for folder in os.listdir(animal_root):
        folder_path = os.path.join(animal_root, folder)
        if os.path.isdir(folder_path):
            photo_dir = os.path.join(folder_path, "photo")
            assert os.path.isdir(photo_dir), f"Missing 'photo' folder in {folder_path}"
            for file in os.listdir(photo_dir):
                assert animal_photo_pattern.match(file), (
                    f"File {file} in {photo_dir} does not match animal naming convention."
                )

def test_crop_media():
    crop_root = os.path.join(MEDIA_ROOT, "crop")
    for folder in os.listdir(crop_root):
        folder_path = os.path.join(crop_root, folder)
        if os.path.isdir(folder_path):
            photo_dir = os.path.join(folder_path, "photo")
            assert os.path.isdir(photo_dir), f"Missing 'photo' folder in {folder_path}"
            for file in os.listdir(photo_dir):
                assert crop_photo_pattern.match(file), (
                    f"File {file} in {photo_dir} does not match crop naming convention."
                )

def test_farm_media():
    farm_root = os.path.join(MEDIA_ROOT, "farm")
    for folder in os.listdir(farm_root):
        folder_path = os.path.join(farm_root, folder)
        if os.path.isdir(folder_path):
            documentary_dir = os.path.join(folder_path, "documentary")
            if os.path.isdir(documentary_dir):
                for file in os.listdir(documentary_dir):
                    assert farm_documentary_pattern.match(file), (
                        f"File {file} in {documentary_dir} does not match documentary naming convention."
                    )
            herovideo_dir = os.path.join(folder_path, "herovideo")
            if os.path.isdir(herovideo_dir):
                for file in os.listdir(herovideo_dir):
                    assert farm_herovideo_pattern.match(file), (
                        f"File {file} in {herovideo_dir} does not match herovideo naming convention."
                    )
            photo_dir = os.path.join(folder_path, "photo")
            if os.path.isdir(photo_dir):
                for file in os.listdir(photo_dir):
                    assert farm_photo_pattern.match(file), (
                        f"File {file} in {photo_dir} does not match farm photo naming convention."
                    )

def test_farmer_media():
    farmer_root = os.path.join(MEDIA_ROOT, "farmer")
    for folder in os.listdir(farmer_root):
        folder_path = os.path.join(farmer_root, folder)
        if os.path.isdir(folder_path):
            photo_dir = os.path.join(folder_path, "photo")
            assert os.path.isdir(photo_dir), f"Missing 'photo' folder in {folder_path}"
            for file in os.listdir(photo_dir):
                assert farmer_photo_pattern.match(file), (
                    f"File {file} in {photo_dir} does not match farmer naming convention."
                )

def test_icons_media():
    icons_root = os.path.join(MEDIA_ROOT, "icons")
    assert os.path.isdir(icons_root), "Icons folder does not exist."
    for file in os.listdir(icons_root):
        assert icons_pattern.match(file), (
            f"Icon file {file} does not match naming convention."
        )

def test_product_media():
    product_root = os.path.join(MEDIA_ROOT, "product")
    for folder in os.listdir(product_root):
        folder_path = os.path.join(product_root, folder)
        if os.path.isdir(folder_path):
            photo_dir = os.path.join(folder_path, "photo")
            assert os.path.isdir(photo_dir), f"Missing 'photo' folder in {folder_path}"
            for file in os.listdir(photo_dir):
                assert product_photo_pattern.match(file), (
                    f"File {file} in {photo_dir} does not match product naming convention."
                )
