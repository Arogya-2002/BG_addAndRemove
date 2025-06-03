import os
import sys
from diffusers import AutoPipelineForInpainting
from diffusers.utils import load_image
import torch

from src.exceptions import CustomException
from src.logger import logging
from src.entity.config import BgConfig, InpaintConfig
from src.entity.artifact import InpaintArtifact
from src.utils import generate_unique_filename  # Utility for unique file naming

# Optimize PyTorch memory behavior
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"

class Inpaint:
    def __init__(self):
        try:
            logging.info("Initializing InpaintConfig and background configuration.")
            self.inpaint_config = InpaintConfig(bg_config=BgConfig())

            logging.info("Detecting device for inference.")
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            logging.info(f"Using device: {self.device}")

            logging.info("Loading inpainting pipeline model.")
            self.pipe = AutoPipelineForInpainting.from_pretrained(
                "diffusers/stable-diffusion-xl-1.0-inpainting-0.1",
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                variant="fp16" if self.device == "cuda" else None
            ).to(self.device)

            # Memory optimizations
            self.pipe.enable_vae_slicing()
            self.pipe.enable_attention_slicing()
            if self.device == "cuda":
                self.pipe.enable_model_cpu_offload()

            logging.info("Pipeline model loaded and memory-optimized.")

        except Exception as e:
            logging.error("Error occurred during Inpaint class initialization.", exc_info=True)
            raise CustomException(e, sys) from e

    def initiate_inpaint(self, mask_img_path: str, input_img_path: str) -> InpaintArtifact:
        try:
            logging.info("Starting inpainting process.")

            # Ensure required folders exist
            os.makedirs(self.inpaint_config.uploaded_path_folder, exist_ok=True)
            os.makedirs(self.inpaint_config.img_path_folder, exist_ok=True)
            os.makedirs(self.inpaint_config.inpaint_output_dir, exist_ok=True)

            target_size = (768, 768)

            logging.info(f"Loading and resizing input image from: {input_img_path}")
            image = load_image(input_img_path).resize(target_size)

            logging.info(f"Loading and resizing mask image from: {mask_img_path}")
            mask_image = load_image(mask_img_path).resize(target_size)

            prompt = "natural seamless fill"
            logging.info(f"Using prompt: {prompt}")

            generator = torch.Generator(device=self.device).manual_seed(0)

            logging.info("Running inpainting model...")
            with torch.inference_mode():
                output_image = self.pipe(
                    prompt=prompt,
                    image=image,
                    mask_image=mask_image,
                    guidance_scale=8.0,
                    num_inference_steps=20,
                    strength=0.99,
                    generator=generator,
                ).images[0]

            output_img_path = generate_unique_filename(
                input_image_path=input_img_path,
                output_folder=self.inpaint_config.inpaint_output_dir
            )

            logging.info(f"Saving output image to: {output_img_path}")
            output_image.save(output_img_path)

            logging.info("Inpainting process completed successfully.")

            return InpaintArtifact(
                mask_img_path=mask_img_path,
                input_img_path=input_img_path,
                output_img_path=output_img_path
            )

        except Exception as e:
            logging.error("Error occurred during inpainting.", exc_info=True)
            raise CustomException(e, sys) from e

        finally:
            del image, mask_image
            if 'output_image' in locals():
                del output_image
            torch.cuda.empty_cache()


# if __name__ == "__main__":
#     try:
#         inpaint_instance = Inpaint()
#         # Example usage
#         mask_path = r"/home/litzchill/vamshi/BG_addAndRemove/data/overture-creations-5sI6fQgYIuo_mask.png"
#         input_path = r"/home/litzchill/vamshi/BG_addAndRemove/data/overture-creations-5sI6fQgYIuo.png"
#         artifact = inpaint_instance.initiate_inpaint(mask_img_path=mask_path, input_img_path=input_path)
#         print(f"Inpainting completed. Output saved at: {artifact.output_img_path}")
#     except CustomException as e:
#         logging.error(f"An error occurred: {e}")
1