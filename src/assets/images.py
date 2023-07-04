from typing import Dict
from assets.asset_model import AssetModel, AssetDict
from logger import logger
import json


class Images:
    _instance = None
    file_path = "src/assets/image_assets.json"

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        # Load the JSON data from file
        with open(self.file_path, 'r') as file:
            json_data = json.load(file)

        # Validate and parse the JSON data using `model_validate_json`
        asset_dict = AssetDict.model_validate(json_data).root
        self.camera_image_data = asset_dict["camera_image"].data
        self.camera_image_mime = asset_dict["camera_image"].mime
        logger.debug(self.camera_image_mime)
