from fletched.routed_app import route
from fletched.mvp import MvpViewBuilder

from ui.screens.details.details_data_source import DetailsDataSource
from ui.screens.details.details_presenter import DetailsPresenter
from ui.screens.details.details_view import DetailsView


@route("/details")
class DetailsViewBuilder(MvpViewBuilder):
    data_source_class = DetailsDataSource
    presenter_class = DetailsPresenter
    view_class = DetailsView
