from fletched.mvp.protocols import MvpViewProtocol, MvpPresenterProtocol
from pydantic import BaseModel


class LoginPresenterProtocol(MvpPresenterProtocol):
    def handle_login(self) -> None:
        ...

    def request_token(self) -> None:
        ...

    def got_to_detail(self) -> None:
        ...


class LoginViewProtocol(MvpViewProtocol):
    def build(self, presenter: LoginPresenterProtocol) -> None:
        ...

    def render(self, model: BaseModel) -> None:
        ...
