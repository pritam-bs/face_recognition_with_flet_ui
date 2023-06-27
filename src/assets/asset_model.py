from pydantic import BaseModel


class AssetModel(BaseModel):
    mime: str
    data: str
