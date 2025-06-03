from src.components.add_bg import AddBg
from src.components.remove_bg import RemoveBg
from src.components.inpaint import Inpaint  

from src.exceptions import CustomException
from src.logger import logging
import sys

def process_remove_bg(input_image_path: str) -> str:
    """Removes background from the given image path and returns path to the saved image."""
    try:
        logging.info(f"Starting background removal for: {input_image_path}")
        remove_bg_obj = RemoveBg()
        artifact = remove_bg_obj.remove_bg(input_image_path)
        return artifact.rmbg_img_path
    except Exception as e:
        logging.error(f"Error while removing background: {e}")
        raise CustomException(e, sys) from e

def process_add_bg(foreground_img_path: str, new_bg_path: str) -> str:
    """Adds new background to a transparent image and returns path to saved image."""
    try:
        logging.info(f"Starting background addition with foreground: {foreground_img_path} and background: {new_bg_path}")
        add_bg_obj = AddBg()
        artifact = add_bg_obj.change_bg(foreground_img_path, new_bg_path)
        return artifact.ch_bg_img_path
    except Exception as e:
        logging.error(f"Error while adding background: {e}")
        raise CustomException(e, sys) from e

def process_inpaint(mask_img_path: str, input_img_path: str) -> str:
    """Applies inpainting to the given image and mask and returns path to saved image."""
    try:
        logging.info(f"Starting inpainting with input: {input_img_path} and mask: {mask_img_path}")
        inpaint_obj = Inpaint()
        artifact = inpaint_obj.initiate_inpaint(mask_img_path=mask_img_path, input_img_path=input_img_path)
        return artifact.output_img_path
    except Exception as e:
        logging.error(f"Error during inpainting: {e}")
        raise CustomException(e, sys) from e


# if __name__ == "__main__":
#     try:
#         # Example test case
#         input_image = r"/home/litzchill/vamshi/BG_addAndRemove/data/overture-creations-5sI6fQgYIuo.png"
#         mask_image = r"/home/litzchill/vamshi/BG_addAndRemove/data/overture-creations-5sI6fQgYIuo_mask.png"
#         new_bg_image = r"/home/litzchill/vamshi/BG_addAndRemove/data/bg1.jpg"

#         # Step 1: Remove background
#         rmbg_path = process_remove_bg(input_image)

#         # Step 2: Add new background
#         final_bg_path = process_add_bg(rmbg_path, new_bg_image)

#         # Step 3: Inpaint the original with a mask
#         inpainted_path = process_inpaint(mask_img_path=mask_image, input_img_path=input_image)

#         print(f"\nBackground removed: {rmbg_path}")
#         print(f"New background added: {final_bg_path}")
#         print(f"Inpainting done: {inpainted_path}")

#     except CustomException as e:
#         logging.error(f"Pipeline error: {e}")
