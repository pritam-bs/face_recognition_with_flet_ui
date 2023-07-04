from pydantic import BaseModel, RootModel
from typing import Dict


class AssetModel(BaseModel):
    mime: str
    data: str


class AssetDict(RootModel):
    root: Dict[str, AssetModel]
