from fletched.routed_app import route
from fletched.mvp import MvpViewBuilder

from ui.screens.login.loging_data_source import LoginDataSource
from ui.screens.login.login_presenter import LoginPresenter
from ui.screens.login.login_view import LoginView


@route("/login")
class LoginViewBuilder(MvpViewBuilder):
    data_source_class = LoginDataSource
    presenter_class = LoginPresenter
    view_class = LoginView
