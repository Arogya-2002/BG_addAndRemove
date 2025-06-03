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

"""constants for image inpainting"""
MASK_IMG_NAME = "mask.png"
INPUT_IMG_NAME = "input_image.png"
INPAINT_OUTPUT_DIR = os.path.join(ARTIFACTS_DIR, "inpainted_images")
INPAINT_OUTPUT_IMG_NAME = "output_image.png"