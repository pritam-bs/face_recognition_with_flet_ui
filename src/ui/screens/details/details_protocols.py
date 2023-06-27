from fletched.mvp.protocols import MvpViewProtocol, MvpPresenterProtocol
from pydantic import BaseModel


class DetailsPresenterProtocol(MvpPresenterProtocol):
    def get_employees(self) -> None:
        ...


class DetailsViewProtocol(MvpViewProtocol):
    def build(self, presenter: DetailsPresenterProtocol) -> None:
        ...

    def render(self, model: BaseModel) -> None:
        ...
