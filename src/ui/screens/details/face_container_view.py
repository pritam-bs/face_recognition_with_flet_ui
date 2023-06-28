import flet
from typing import Protocol, Dict
from typing import Callable
from data_models.employee import Meal, Employee
from typing import Optional
from flet_core.ref import Ref
from assets.images import Images
import time
import rx
from typing import Union


class FaceContainerProtocol(Protocol):
    def on_meal_select(meal: Meal):
        ...


class FaceContainerView(flet.UserControl, FaceContainerProtocol):
    MealSelectCallable = Callable[[any, Meal], None]

    def __init__(self, on_meal_select: MealSelectCallable, ref: Optional[Ref], expand: Union[None, bool, int] = None):
        super().__init__(ref=ref, expand=expand)
        self.greetings_ref = flet.Ref[flet.Text]()
        self.breakfast_progress_ring_ref = flet.Ref[flet.ProgressRing]()
        self.lunch_progress_ring_ref = flet.Ref[flet.ProgressRing]()
        self.breakfast_button_ref = flet.Ref[flet.ElevatedButton]()
        self.lunch_button_ref = flet.Ref[flet.ElevatedButton]()
        self.on_meal_select = on_meal_select
        self.frame_image_ref = flet.Ref[flet.Image]()
        self.meal_info_timestamp = None

    def did_mount(self):
        self._start_meal_info_timmer()

    def will_unmount(self):
        self.meal_info_subscription.dispose()

    def build(self):
        return flet.Column(
            controls=[
                flet.Text("Scan your face",
                          style=flet.TextThemeStyle.TITLE_LARGE
                          ),
                flet.Image(
                    ref=self.frame_image_ref,
                    src_base64=Images().camera_image_data,
                    width=200,
                    height=200,
                    border_radius=10,
                    fit=flet.ImageFit.COVER,
                ),
                flet.Container(
                    content=flet.Container(
                        content=self._get_meal_info_control(),
                        expand=False,
                        width=400,
                        height=150,
                        alignment=flet.alignment.top_center,
                        padding=20,
                        border_radius=10,
                        bgcolor=flet.colors.BLUE_GREY_800,
                    ),
                    expand=True,
                    alignment=flet.alignment.top_center,
                    padding=20,
                    border_radius=10,
                    bgcolor=flet.colors.BLUE_GREY_900,
                ),
            ],
            alignment=flet.MainAxisAlignment.CENTER,
            horizontal_alignment=flet.CrossAxisAlignment.CENTER,
            expand=True,
        )

    def _get_meal_info_control(self):
        return flet.Column(
            controls=[
                flet.Text("Hello Name of the employee",
                          style=flet.TextThemeStyle.TITLE_MEDIUM,
                          ref=self.greetings_ref),
                flet.Text("What meal do you want to consume?",
                          style=flet.TextThemeStyle.TITLE_SMALL),
                flet.Row(
                    controls=[
                        flet.ElevatedButton(
                            ref=self.breakfast_button_ref,
                            content=flet.Row(controls=[
                                flet.Text("Breakfast"),
                                flet.ProgressRing(
                                    ref=self.breakfast_progress_ring_ref,
                                    height=20,
                                    width=20,
                                    visible=False,
                                ),
                            ],
                                vertical_alignment=flet.CrossAxisAlignment.CENTER,
                                alignment=flet.MainAxisAlignment.CENTER,
                            ),
                            width=150,
                            height=40,
                            on_click=self._breakfast_button_on_click
                        ),
                        flet.ElevatedButton(
                            ref=self.lunch_button_ref,
                            content=flet.Row(controls=[
                                flet.Text("Lunch"),
                                flet.ProgressRing(
                                    ref=self.lunch_progress_ring_ref,
                                    height=20,
                                    width=20,
                                    visible=False,
                                ),
                            ],
                                vertical_alignment=flet.CrossAxisAlignment.CENTER,
                                alignment=flet.MainAxisAlignment.CENTER,
                            ),
                            width=150,
                            height=40,
                            on_click=self._lunch_button_on_click
                        ),
                    ],
                    alignment=flet.MainAxisAlignment.START,
                    vertical_alignment=flet.CrossAxisAlignment.CENTER,
                    expand=False,
                )
            ],
            expand=False,
            alignment=flet.MainAxisAlignment.START,
            horizontal_alignment=flet.CrossAxisAlignment.START,
        )

    def _get_consumed_meal_info_control(self):
        pass

    def _breakfast_button_on_click(self, e):
        self.breakfast_progress_ring_ref.current.visible = True
        self.breakfast_button_ref.current.disabled = True
        self.lunch_button_ref.current.disabled = True
        self.update()
        self.on_meal_select(Meal.BREAKFAST)

    def _lunch_button_on_click(self, e):
        self.lunch_progress_ring_ref.current.visible = True
        self.breakfast_button_ref.current.disabled = True
        self.lunch_button_ref.current.disabled = True
        self.update()
        self.on_meal_select(Meal.LUNCH)

    def update_frame_image(self, image_base64):
        if self.frame_image_ref.current is not None and image_base64 is not None:
            self.frame_image_ref.current.src_base64 = image_base64
            self.update()

    def _show_meal_info(self, employee_info):
        self.meal_info_timestamp = time.time()
        pass

    def _hide_meal_info(self, tick):
        if self.meal_info_timestamp is None:
            return
        # Calculate the difference in seconds
        diff_seconds = time.time() - self.meal_info_timestamp
        if diff_seconds > 10:
            pass

    def _start_meal_info_timmer(self):
        self.meal_info_observable = rx.interval(1.0)
        self.meal_info_subscription = self.meal_info_observable.subscribe(
            on_next=self._hide_meal_info)
