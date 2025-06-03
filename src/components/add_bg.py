from src.exceptions import CustomException
from src.logger import logging
from src.entity.config import BgConfig, ChangeBgConfig
from src.entity.artifact import ChangeBgArtifact
from src.utils import generate_unique_filename

import sys
from PIL import Image
import os
import shutil

class AddBg:
    def __init__(self):
        try:
            self.change_bg_config = ChangeBgConfig(bg_config=BgConfig())
        except Exception as e:
            raise CustomException(e, sys)

    def change_bg(self, img_path: str, bg_img_path: str) -> ChangeBgArtifact:
        try:
            logging.info("Changing background of the image.")

            # Load foreground and background
            foreground = Image.open(img_path).convert("RGBA")
            background = Image.open(bg_img_path).convert("RGBA")
            background = background.resize(foreground.size)

            # Composite images
            combined = Image.alpha_composite(background, foreground)

            # Ensure output folders exist
            os.makedirs(self.change_bg_config.img_path_folder, exist_ok=True)
            os.makedirs(self.change_bg_config.uploaded_path_folder, exist_ok=True)  # ✅ Ensure uploaded folder exists

            # Save the combined image
            output_image_path = generate_unique_filename(
                img_path,
                self.change_bg_config.img_path_folder
            )
            combined.save(output_image_path)

            # ✅ Save the uploaded background for reference
            uploaded_bg_path = generate_unique_filename(
                bg_img_path,
                self.change_bg_config.uploaded_path_folder
            )
            shutil.copy(bg_img_path, uploaded_bg_path)

            logging.info(f"Background changed and saved to: {output_image_path}")
            logging.info(f"Uploaded background saved to: {uploaded_bg_path}")

            return ChangeBgArtifact(ch_bg_img_path=output_image_path)

        except Exception as e:
            logging.error(f"Failed to change background: {e}")
            raise CustomException(e, sys)
if __name__ == "__main__":
    add_bg_obj = AddBg()
    add_bg_obj.change_bg(
        img_path=r"C:\Users\Vamshi\Desktop\Projects\litzchill\remove_bg\artifacts\removed_bg_images\sky2_rmbg_1748686518.png",
        bg_img_path=r"C:\Users\Vamshi\Desktop\Projects\litzchill\remove_bg\data\bg1.jpg"
    )
