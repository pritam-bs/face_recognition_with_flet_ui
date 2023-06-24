import flet

from pydantic import BaseModel
from fletched.mvp import MvpView, ViewConfig

from ui.screens.details.details_protocols import DetailsPresenterProtocol, DetailsViewProtocol
from ui.screens.details.info_sidebar_view import InfoSidebarView
from ui.screens.details.face_container_view import FaceContainerView
from ui.screens.details.face_container_view import Meal
from ui.screens.details.employees import employees
import base64

from flet import (
    Icon,
    Text,
    TextField,
    colors,
    icons,
    ElevatedButton,
)


class DetailsView(MvpView, DetailsViewProtocol):
    progress_ring_ref = flet.Ref[flet.ProgressRing]()
    face_container_view_ref = flet.Ref[FaceContainerView]()

    ref_map = {

    }

    config = ViewConfig(
        vertical_alignment=flet.MainAxisAlignment.START,
        horizontal_alignment=flet.CrossAxisAlignment.START,
        appbar=flet.AppBar(
            leading=Icon(icons.GRID_GOLDENRATIO_ROUNDED),
            leading_width=40,
            title=Text("Access Control Console",
                       style=flet.TextThemeStyle.TITLE_LARGE),
            center_title=False,
            toolbar_height=50,
        )
    )

    def build(self, presenter: DetailsPresenterProtocol) -> None:
        self.presenter = presenter
        self.info_sidebar_view = InfoSidebarView()
        ui = self._get_ui(info_sidebar_view=self.info_sidebar_view)
        self.controls.append(ui)

    def render(self, model: BaseModel) -> None:
        super().render(model)
        model_map = model.dict()
        is_loading = model_map["is_loading"]
        # self.progress_ring_ref.current.visible = is_loading

        if self.face_container_view_ref.current is not None:
            image_base64 = model_map["frame_image_base64"]
            self.face_container_view_ref.current.update_frame_image(
                image_base64=image_base64)

    def _get_ui(self, info_sidebar_view: InfoSidebarView) -> flet.Row:
        return flet.Row(controls=[
            flet.Container(
                info_sidebar_view,
                expand=False,
            ),
            flet.Container(
                FaceContainerView(on_meal_select=self.on_meal_select,
                                  ref=self.face_container_view_ref),
                expand=True,
                alignment=flet.alignment.center,
            )
        ],
            vertical_alignment=flet.CrossAxisAlignment.START,
            alignment=flet.MainAxisAlignment.START,
            expand=True,
        )

    def on_meal_select(self, meal: Meal):
        pass
