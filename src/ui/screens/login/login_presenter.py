from dataclasses import dataclass
from fletched.mvp import MvpPresenter
from ui.screens.login.login_protocols import LoginViewProtocol, LoginPresenterProtocol
from ui.screens.login.loging_data_source import LoginDataSource


@dataclass
class LoginPresenter(MvpPresenter, LoginPresenterProtocol):
    data_source: LoginDataSource
    view: LoginViewProtocol

    def handle_login(self) -> None:
        self.data_source.login()

    def got_to_detail(self) -> None:
        self.data_source.got_to_details()
