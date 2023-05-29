from typing import Protocol
from fletched.mvp.protocols import MvpViewProtocol, MvpPresenterProtocol
from pydantic import BaseModel


class LoginPresenterProtocol(MvpPresenterProtocol):
    def handle_login(self) -> None:
        ...


class LoginViewProtocol(MvpViewProtocol):
    def build(self, presenter: LoginPresenterProtocol) -> None:
        ...

    def render(self, model: BaseModel) -> None:
        ...
