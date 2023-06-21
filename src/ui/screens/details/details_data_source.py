from fletched.mvp import MvpDataSource
from fletched.mvp import MvpModel, ErrorMessage
from typing import Optional


class DetailsModel(MvpModel):
    is_loading: Optional[bool] = False


class DetailsDataSource(MvpDataSource):
    current_model = DetailsModel()
