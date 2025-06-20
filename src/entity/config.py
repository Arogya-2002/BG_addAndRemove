from src.exceptions import CustomException
from src.logger import logging
import sys


from src.constants import *

class BgConfig:
    def __init__(self):
        self.rmbg_img_name = RMBG_IMG_NAME
        self.bg_img_name = BG_IMG_NAME
        self.ch_bg_img_name = CH_BG_IMG_NAME
        self.img_path_folder = IMG_PATH_FOLDER
        self.removed_bg_dir = REMOVED_BG_DIR
        self.changed_bg_dir = CHANGED_BG_DIR
        self.uploaded_bg_dir = UPLOADED_BG_DIR



class RemoveBgConfig:
    def __init__(self,bg_config:BgConfig):
        self.rmbg_img_name = bg_config.rmbg_img_name
        self.bg_img_name = bg_config.bg_img_name
        self.img_path_folder = bg_config.removed_bg_dir


class ChangeBgConfig:
    def __init__(self, bg_config: BgConfig):
        self.ch_bg_img_name = bg_config.ch_bg_img_name
        self.img_path_folder = bg_config.changed_bg_dir
        self.bg_img_name = bg_config.bg_img_name
        self.uploaded_path_folder: str = bg_config.uploaded_bg_dir


