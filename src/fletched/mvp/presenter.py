from dataclasses import dataclass

from fletched.mvp.datasource import MvpDataSource
from fletched.mvp.protocols import MvpViewProtocol
from logger import logger


@dataclass
class MvpPresenter:
    data_source: MvpDataSource
    view: MvpViewProtocol

    def __post_init__(self) -> None:
        if self.__class__ == MvpPresenter:
            raise TypeError("Cannot instantiate abstract class.")
        self.data_source.register(self.update_view)

    def build(self) -> None:
        view = self.view()
        if view is not None:
            view.build(self)
        else:
            logger.debug("View distroyed")

    def update_view(self) -> None:
        view = self.view()
        if view is not None:
            view.render(self.data_source.current_model)
        else:
            logger.debug("View distroyed")
        del self.data_source.current_model
