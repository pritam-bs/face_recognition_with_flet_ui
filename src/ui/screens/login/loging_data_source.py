from fletched.mvp import MvpDataSource
from fletched.mvp import MvpModel, ErrorMessage
from ui.app import App
from pydantic import validator


class LoginModel(MvpModel):
    text_field: ErrorMessage | int = 0
    is_loading: bool = False

    @validator('text_field')
    def id_must_be_4_digits(cls, value):
        if isinstance(value, ErrorMessage):
            return value
        if len(str(value)) != 4:
            raise ValueError('must be 4 digits')
        return value


class LoginDataSource(MvpDataSource):
    current_model = LoginModel()

    def __init__(self, *, app: App | None, route_params: dict[str, str]) -> None:
        super().__init__(app=app, route_params=route_params)
        self.app = app

    def login(self) -> None:
        self.update_model_complete({"text_field": 12,
                                    "is_loading": not self.current_model.is_loading,
                                    })
