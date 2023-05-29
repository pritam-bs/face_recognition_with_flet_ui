import flet
from enum import Enum

from pydantic import BaseModel
from fletched.mvp import MvpView, ViewConfig
from flet import (
    Icon,
    Text,
    TextField,
    colors,
    icons,
    ElevatedButton,
)

from ui.screens.login.login_protocols import LoginPresenterProtocol, LoginViewProtocol


class LoginView(MvpView, LoginViewProtocol):
    progress_ring_ref = flet.Ref[flet.ProgressRing]()
    alert_dialog_ref = flet.Ref[flet.AlertDialog]()
    ref_map = {
        "text_field": flet.Ref[flet.TextField](),
    }

    config = ViewConfig(
        vertical_alignment=flet.MainAxisAlignment.CENTER,
        horizontal_alignment=flet.CrossAxisAlignment.CENTER,
        appbar=flet.AppBar(
            leading=Icon(icons.GRID_GOLDENRATIO_ROUNDED),
            leading_width=100,
            title=Text("Face Recognition",
                       style=flet.TextThemeStyle.TITLE_LARGE),
            center_title=False,
            toolbar_height=75,
        )
    )

    def build(self, presenter: LoginPresenterProtocol) -> None:
        self.presenter = presenter
        ui = self._get_ui()
        self.controls.append(ui)

    def render(self, model: BaseModel) -> None:
        model_map = model.dict()
        is_loading = model_map["is_loading"]
        self.progress_ring_ref.current.visible = is_loading
        super().render(model)

    def _get_ui(self) -> flet.Stack:
        return flet.Stack(controls=[
            flet.Column(controls=[
                Text(value="Hello"),
                TextField(ref=self.ref_map["text_field"]),
                ElevatedButton(
                    content=flet.Row(controls=[
                        Text("Login"),
                        flet.ProgressRing(
                            ref=self.progress_ring_ref, height=20, width=20),
                    ],
                        vertical_alignment=flet.CrossAxisAlignment.CENTER,
                        alignment=flet.MainAxisAlignment.CENTER,

                    ),
                    width=200,
                    height=40,
                    on_click=self._login_button_on_click
                ),
            ])
        ])

    def _get_alert_dialog(self) -> flet.AlertDialog:
        dlg_modal = flet.AlertDialog(
            ref=self.alert_dialog_ref,
            modal=True,
            title=flet.Text("Please confirm"),
            content=flet.Text("Do you really want to delete all those files?"),
            actions=[
                flet.TextButton("Confirm", on_click=self.confirm_action),
                flet.TextButton("Cancle", on_click=self.cancle_action),
            ],
            actions_alignment=flet.MainAxisAlignment.END,
            on_dismiss=lambda e: print("Modal dialog dismissed!"),
        )
        return dlg_modal

    def confirm_action(self, e):
        self.alert_dialog_ref.current.open = False
        self.page.update()
        self.presenter.handle_login()

    def cancle_action(self, e):
        self.alert_dialog_ref.current.open = False
        self.page.update()

    def _login_button_on_click(self, e) -> None:
        self.page.dialog = self._get_alert_dialog()
        self.alert_dialog_ref.current.open = True
        self.page.update()
