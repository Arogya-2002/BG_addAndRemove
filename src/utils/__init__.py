# utils.py
import os
from pathlib import Path
import time,io

def generate_unique_filename(input_image_path: str, output_folder: str) -> str:
    """
    Generates a unique filename for the background removed image.
    
    Parameters:
        input_image_path (str): The path of the original input image.
        output_folder (str): The folder where the processed image will be saved.
    
    Returns:
        str: A unique output file path.
    """
    input_stem = Path(input_image_path).stem  # Extracts the base filename without extension
    timestamp = int(time.time())  # Current time in seconds
    unique_name = f"{input_stem}_rmbg_{timestamp}.png"
    return os.path.join(output_folder, unique_name)
