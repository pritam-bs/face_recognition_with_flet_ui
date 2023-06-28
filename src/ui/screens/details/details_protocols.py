from fletched.mvp.protocols import MvpViewProtocol, MvpPresenterProtocol
from pydantic import BaseModel
from data_models.employee import Meal


class DetailsPresenterProtocol(MvpPresenterProtocol):
    def get_employees(self) -> None:
        ...

    def submit_meal_consumption(self, employee_id: str, meal: Meal) -> None:
        ...


class DetailsViewProtocol(MvpViewProtocol):
    def build(self, presenter: DetailsPresenterProtocol) -> None:
        ...

    def render(self, model: BaseModel) -> None:
        ...
