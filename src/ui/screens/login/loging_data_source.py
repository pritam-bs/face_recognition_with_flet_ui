from fletched.mvp import MvpDataSource
from fletched.mvp import MvpModel, ErrorMessage
from ui.app import App
from pydantic import validator
from flet.auth.providers.google_oauth_provider import GoogleOAuthProvider
from settings import settings
from httpx import HTTPStatusError
from api.api_client import APIClient
from rx.subject.asyncsubject import AsyncSubject
from pydantic import BaseModel
from logger import logger
from src.auth.auth_client import OAuthClient, AuthorizationResponse
from typing import Optional, Union, Dict


class MessageModel(BaseModel):
    msg: str


class LoginModel(MvpModel):
    is_loading: Optional[bool] = None
    verification_url: Optional[str] = None
    expires_in: Optional[int] = None
    user_code: Optional[str] = None


class LoginDataSource(MvpDataSource):
    current_model = LoginModel()
    # Create an instance of the APIClient
    api_client = APIClient.create("http://demo6931875.mockable.io")
    auth_client = OAuthClient()

    def __init__(self, *, app: Union[App, None], route_params: Dict[str, str]) -> None:
        super().__init__(app=app, route_params=route_params)
        self.app = app

    def login(self) -> None:
        self.update_model_complete(
            new_model={
                "is_loading": True
            }
        )
        response: AuthorizationResponse = self.auth_client.request_codes()
        self.update_model_complete(new_model={"verification_url": response.verification_url,
                                              "expires_in": response.expires_in,
                                              "user_code": response.user_code,
                                              "is_loading": False})

    def api_call(self) -> None:
        self.update_model_complete(changes={"is_loading": True})
        # Configure the request
        self.api_client.get().set_path("/msg")

        # Make the API call and get the observable
        observable: AsyncSubject = self.api_client.make_request(
            model_type=MessageModel)

        # Subscribe to the observable to receive the API response
        def on_next(data):
            logger.debug(data)
            self.update_model_partial(changes={"is_loading": False})

        def on_error(error):
            logger.debug(error)
            self.update_model_partial(changes={"is_loading": False})

        observable.subscribe(on_next=on_next, on_error=on_error).dispose()

    def got_to_details(self):
        self.page.go("/details")
