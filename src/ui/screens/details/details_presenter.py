from dataclasses import dataclass
from fletched.mvp import MvpPresenter
from ui.screens.details.details_protocols import DetailsViewProtocol, DetailsPresenterProtocol
from ui.screens.details.details_data_source import DetailsDataSource


@dataclass
class DetailsPresenter(MvpPresenter, DetailsPresenterProtocol):
    data_source: DetailsDataSource
    view: DetailsViewProtocol
