from src.exceptions import CustomException
import sys
from src.logger import logging

from src.entity.config import BgConfig, RemoveBgConfig
from src.entity.artifact import RemoveBgArtifact
from src.utils import generate_unique_filename

from rembg import remove, new_session
from PIL import Image
import os

class RemoveBg:
    def __init__(self):
        try:
            self.remove_bg_config = RemoveBgConfig(bg_config=BgConfig())
        except Exception as e:
            raise CustomException(e, sys)

    def remove_bg(self, input_image_path: str) -> RemoveBgArtifact:
        try:
            logging.info(f"Removing background from image: {input_image_path}")
            input_image = Image.open(input_image_path)

            # Create session with specific model
            session = new_session(model_name='u2net_human_seg')

            output_image = remove(
                input_image,
                session=session,
                alpha_matting=True,
                alpha_matting_foreground_threshold=240,
                alpha_matting_background_threshold=10,
                alpha_matting_erode_size=5
            )

            # Ensure specific folder exists
            os.makedirs(self.remove_bg_config.img_path_folder, exist_ok=True)

            # Generate unique filename
            output_image_path = generate_unique_filename(
                input_image_path,
                self.remove_bg_config.img_path_folder
            )

            # Save final output image
            output_image.save(output_image_path)

            logging.info(f"Background removed and saved to: {output_image_path}")

            return RemoveBgArtifact(rmbg_img_path=output_image_path)

        except Exception as e:
            logging.error(f"Error in removing background: {e}")
            raise CustomException(e, sys) from e


# if __name__ == "__main__":
#     remove_bg_obj = RemoveBg()
#     remove_bg_obj.remove_bg(
#         r"C:\Users\Vamshi\Desktop\Projects\litzchill\remove_bg\data\sky2.jpg"
#     )
