# from pydantic import BaseModel, RootModel
from pydantic import BaseModel
from typing import Dict


class AssetModel(BaseModel):
    mime: str
    data: str


# class AssetDict(RootModel):
#     root: Dict[str, AssetModel]

class AssetDict(BaseModel):
    __root__: Dict[str, AssetModel]
