from pydantic import parse_file_as
from typing import Dict
from assets.asset_model import AssetModel
from logger import logger


class Images:
    _instance = None
    file_path = "src/assets/image_assets.json"

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self.image = parse_file_as(Dict[str, AssetModel], path=self.file_path)
        self.camera_image_data = self.image["camera_image"].data
        self.camera_image_mime = self.image["camera_image"].mime
        logger.debug(self.camera_image_mime)
