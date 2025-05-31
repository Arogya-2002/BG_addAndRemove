import os

# Root artifact directory
ARTIFACTS_DIR = "artifacts"

# Subdirectories
REMOVED_BG_DIR = os.path.join(ARTIFACTS_DIR, "removed_bg_images")
CHANGED_BG_DIR = os.path.join(ARTIFACTS_DIR, "changed_bg_images")
UPLOADED_BG_DIR = os.path.join(ARTIFACTS_DIR, "user_uploaded_bg_images")

# Image filenames
RMBG_IMG_NAME = "removed_bg.png"
BG_IMG_NAME = "background.png"
CH_BG_IMG_NAME = "changed_bg.png"

# Default path folder (can be anything general)
IMG_PATH_FOLDER = ARTIFACTS_DIR
