from dataclasses import dataclass
from fletched.mvp import MvpPresenter
from ui.screens.details.details_protocols import DetailsViewProtocol, DetailsPresenterProtocol
from ui.screens.details.details_data_source import DetailsDataSource
from data_models.employee import Meal


@dataclass
class DetailsPresenter(MvpPresenter, DetailsPresenterProtocol):
    data_source: DetailsDataSource
    view: DetailsViewProtocol

    def get_employees(self) -> None:
        self.data_source.get_employees_info()

    def submit_meal_consumption(self, employee_id: str, meal: Meal) -> None:
        self.data_source.submit_meal_consumption(
            employee_id=employee_id, meal=meal)
