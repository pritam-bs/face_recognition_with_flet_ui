import flet

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
import qrcode
import base64
from io import BytesIO
import time

from ui.screens.login.login_protocols import LoginPresenterProtocol, LoginViewProtocol


class LoginView(MvpView, LoginViewProtocol):
    progress_ring_ref = flet.Ref[flet.ProgressRing]()
    alert_dialog_ref = flet.Ref[flet.AlertDialog]()
    qr_image_ref = flet.Ref[flet.Image]()
    count_down_text_ref = flet.Ref[flet.Text]()
    ref_map = {

    }

    config = ViewConfig(
        vertical_alignment=flet.MainAxisAlignment.CENTER,
        horizontal_alignment=flet.CrossAxisAlignment.CENTER,
        appbar=flet.AppBar(
            leading=Icon(icons.GRID_GOLDENRATIO_ROUNDED),
            leading_width=100,
            title=Text("Access Control Console",
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
        super().render(model)
        model_map = model.dict()
        is_loading = model_map["is_loading"]
        self.progress_ring_ref.current.visible = is_loading

        verification_url = model_map["verification_url"]
        expires_in = model_map["expires_in"]
        user_code = model_map["user_code"]
        if verification_url is not None and expires_in is not None and user_code is not None:
            self._show_qr_dialog(
                verification_url=verification_url, expires_in=expires_in, user_code=user_code)

    def _get_ui(self) -> flet.Column:
        return flet.Column(controls=[
            Text(value="Welcome to the access control console. \nLog in with a user that has access control device privilege."),
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
            ElevatedButton(
                content=Text("Go To Detail"),
                width=300,
                height=40,
                on_click=self._got_to_detail,
            ),
        ],
            alignment=flet.MainAxisAlignment.CENTER,
            horizontal_alignment=flet.CrossAxisAlignment.CENTER
        )

    def _show_qr_dialog(self, verification_url: str, expires_in: int, user_code: str) -> flet.AlertDialog:
        qr_image_data = qrcode.make(verification_url)
        byte_stream = BytesIO()
        qr_image_data.save(byte_stream)
        base64_data = base64.b64encode(byte_stream.getvalue()).decode('utf-8')

        qr_dialog = flet.AlertDialog(
            ref=self.alert_dialog_ref,
            modal=True,
            title=flet.Text(
                "Scan the QR code and complete the proress from your phone and then press Confirm button"),
            content=flet.Card(
                content=flet.Container(
                    content=flet.Column(
                        [
                            flet.Image(
                                src_base64=base64_data,
                                width=200,
                                height=200,
                                fit=flet.ImageFit.FIT_WIDTH,
                                repeat=flet.ImageRepeat.NO_REPEAT,
                                border_radius=flet.border_radius.all(10),
                            ),
                            flet.Card(
                                content=flet.Container(
                                    content=flet.Row(
                                        [
                                            Text(
                                                "Code:",
                                                size=40,
                                            ),
                                            Text(
                                                user_code,
                                                size=40,
                                            ),
                                        ],
                                        expand=False,
                                        vertical_alignment=flet.CrossAxisAlignment.CENTER,
                                        alignment=flet.MainAxisAlignment.CENTER,
                                    ),
                                    expand=False,
                                    # width=200,
                                    height=100,
                                ),
                                expand=False,
                            ),
                            Text(
                                ref=self.count_down_text_ref,
                                value="",
                            )
                        ],
                        expand=False,
                        alignment=flet.MainAxisAlignment.CENTER,
                        horizontal_alignment=flet.CrossAxisAlignment.CENTER
                    )
                )
            ),
            actions=[
                flet.TextButton("Confirm", on_click=self.confirm_action),
                flet.TextButton("Cancel", on_click=self.cancle_action),
            ],
            actions_alignment=flet.MainAxisAlignment.END,
            on_dismiss=lambda e: print("Modal dialog dismissed!"),
        )
        self.page.dialog = qr_dialog
        self.page.dialog.open = True
        self.page.update()
        self.countdown(seconds=expires_in)

    def confirm_action(self, e):
        self.alert_dialog_ref.current.open = False
        self.page.update()
        self._request_token()

    def cancle_action(self, e):
        self.alert_dialog_ref.current.open = False
        self.page.update()

    def countdown(self, seconds):
        start_time = time.time()
        end_time = start_time + seconds

        while time.time() < end_time:
            if self.alert_dialog_ref.current.open == False:
                break
            remaining_seconds = int(end_time - time.time())
            minutes, secs = divmod(remaining_seconds, 60)
            timer = '{:02d}:{:02d}'.format(minutes, secs)
            self.count_down_text_ref.current.value = timer
            self.page.update()

    def _login_button_on_click(self, e) -> None:
        self.presenter.handle_login()

    def _request_token(self):
        self.presenter.request_token()

    def _got_to_detail(self, e):
        self.presenter.got_to_detail()
