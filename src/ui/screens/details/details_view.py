import flet

from pydantic import BaseModel, parse_obj_as
from typing import List
from data_models.employee import Employee
from fletched.mvp import MvpView, ViewConfig

from ui.screens.details.details_protocols import DetailsPresenterProtocol, DetailsViewProtocol
from ui.screens.details.info_sidebar_view import InfoSidebarView
from ui.screens.details.face_container_view import FaceContainerView
from ui.screens.details.face_container_view import Meal
import base64
from app_errors.app_error import ErrorModel


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
    info_sidebar_view_ref = flet.Ref[InfoSidebarView]()
    face_container_view_ref = flet.Ref[FaceContainerView]()
    error_dialog_ref = flet.Ref[flet.AlertDialog]()
    no_meal_dialog_ref = flet.Ref[flet.AlertDialog]()

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
        ui = self._get_ui()
        self.controls.append(ui)

    def render(self, model: BaseModel) -> None:
        super().render(model)
        model_map = model.dict()

        is_loading = model_map["is_loading"]
        if is_loading is not None:
            self.info_sidebar_view_ref.current.update_progress_view(
                is_in_progress=is_loading)

        if self.face_container_view_ref.current is not None:
            image_base64 = model_map["frame_image_base64"]
            self.face_container_view_ref.current.update_frame_image(
                image_base64=image_base64)

        if model_map["employee_list"] is not None:
            employees = parse_obj_as(
                List[Employee], model_map["employee_list"])
            if employees is not None and self.info_sidebar_view_ref.current is not None:
                self.info_sidebar_view_ref.current.update_list(
                    employee_list=employees)

        app_error = model_map["app_error"]
        if app_error is not None:
            content = app_error["content"]
            error_message = content["message"] if content is not None and content["message"] is not None else "Unknown error"
            self._show_error_dialog(description=error_message)

        if model_map["no_meal_found"] is not None:
            employee_id = model_map["no_meal_found"]
            if self.face_container_view_ref.current is not None:
                self.face_container_view_ref.current.show_booking_not_found_info(
                    employee_id=employee_id)

        if model_map["meal_found"] is not None:
            employee_info = parse_obj_as(Employee, model_map["meal_found"])
            if self.face_container_view_ref.current is not None:
                self.face_container_view_ref.current.show_meal_info(
                    employee_info=employee_info)

    def _get_ui(self) -> flet.Row:
        return flet.Row(controls=[
            InfoSidebarView(presenter=self.presenter,
                            ref=self.info_sidebar_view_ref),
            FaceContainerView(on_meal_select=self.on_meal_select,
                              ref=self.face_container_view_ref,
                              expand=True),

        ],
            vertical_alignment=flet.CrossAxisAlignment.START,
            alignment=flet.MainAxisAlignment.START,
            expand=True,
        )

    def _show_error_dialog(self, description: str):
        error_dialog = flet.AlertDialog(
            ref=self.error_dialog_ref,
            modal=True,
            title=flet.Text(
                "An Exception Has Occurred"),
            content=flet.Text(
                f"An error has occurred while processing your request.\nDescription: {description}"
            ),
            actions=[
                flet.TextButton(
                    "Cancel", on_click=self._error_dialog_cancle_action),
            ],
            actions_alignment=flet.MainAxisAlignment.END,
            on_dismiss=lambda e: print("Error dialog dismissed!"),
        )
        self.page.dialog = error_dialog
        self.page.dialog.open = True
        self.page.update()

    def _error_dialog_cancle_action(self, e):
        self.error_dialog_ref.current.open = False
        self.page.update()

    def on_meal_select(self, meal: Meal):
        pass
