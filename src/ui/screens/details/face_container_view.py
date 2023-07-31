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


class FaceContainerView(flet.UserControl):
    MealSelectCallable = Callable[[any, Employee, Meal], None]
    is_mounted = False

    def __init__(self, on_meal_select: MealSelectCallable, ref: Optional[Ref], expand: Union[None, bool, int] = None):
        super().__init__(ref=ref, expand=expand)

        self.breakfast_progress_ring_ref = flet.Ref[flet.ProgressRing]()
        self.lunch_progress_ring_ref = flet.Ref[flet.ProgressRing]()
        self.breakfast_button_ref = flet.Ref[flet.ElevatedButton]()
        self.lunch_button_ref = flet.Ref[flet.ElevatedButton]()

        self.frame_image_ref = flet.Ref[flet.Image]()
        self.meal_info_container_ref = flet.Ref[flet.Container]()

        self.on_meal_select = on_meal_select
        self.meal_info_timestamp = None
        self.currently_showing_employee = None

    def did_mount(self):
        self.is_mounted = True
        self._start_meal_info_timmer()

    def will_unmount(self):
        self.is_mounted = False
        self.meal_info_subscription.dispose()

    def build(self):
        return flet.Column(
            controls=[
                flet.Text(
                    "Face Scanner",
                    style=flet.TextThemeStyle.DISPLAY_SMALL,
                    color=flet.colors.SECONDARY,
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
                        ref=self.meal_info_container_ref,
                        content=self._get_description_control(),
                        expand=False,
                        width=400,
                        height=150,
                        alignment=flet.alignment.top_center,
                        padding=20,
                        border_radius=10,
                        bgcolor=flet.colors.ON_SECONDARY,
                    ),
                    expand=True,
                    alignment=flet.alignment.top_center,
                    padding=20,
                    border_radius=10,
                    bgcolor=flet.colors.SECONDARY_CONTAINER,
                ),
            ],
            alignment=flet.MainAxisAlignment.CENTER,
            horizontal_alignment=flet.CrossAxisAlignment.CENTER,
            expand=True,
        )

    def _get_meal_info_control(self, employee_name: str, is_breakfast_disable: bool, is_lunch_disable: bool):
        return flet.Column(
            controls=[
                flet.Text(
                    f"Hello {employee_name}",
                    style=flet.TextThemeStyle.TITLE_MEDIUM,
                    color=flet.colors.SECONDARY,
                ),
                flet.Text(
                    "What meal do you want to consume?",
                    style=flet.TextThemeStyle.TITLE_SMALL,
                    color=flet.colors.SECONDARY,
                ),

                flet.Row(
                    controls=[
                        flet.ElevatedButton(
                            ref=self.breakfast_button_ref,
                            content=flet.Row(controls=[
                                flet.Text(
                                    "Breakfast",
                                ),
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
                            disabled=is_breakfast_disable,
                            on_click=self._breakfast_button_on_click
                        ),
                        flet.ElevatedButton(
                            ref=self.lunch_button_ref,
                            content=flet.Row(controls=[
                                flet.Text(
                                    "Lunch",
                                ),
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
                            disabled=is_lunch_disable,
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

    def _get_description_control(self):
        return flet.Column(
            controls=[
                flet.Text(
                    "Welcome to office meal service!",
                    style=flet.TextThemeStyle.TITLE_LARGE,
                    color=flet.colors.SECONDARY,
                ),
                flet.Text(
                    "Please scan your face to access the meal options.",
                    style=flet.TextThemeStyle.TITLE_MEDIUM,
                    color=flet.colors.SECONDARY,
                ),

            ]
        )

    def _get_booking_not_found_control(self, employee_id: str):
        return flet.Column(
            controls=[
                flet.Text(
                    "We apologize for any inconvenience caused, but it appears that you have not booked a meal for today.",
                    style=flet.TextThemeStyle.BODY_LARGE,
                    color=flet.colors.ON_ERROR_CONTAINER,
                ),
                flet.Text(
                    f"Employee ID: {employee_id}",
                    style=flet.TextThemeStyle.TITLE_LARGE,
                    color=flet.colors.ON_ERROR_CONTAINER,
                ),
            ]
        )

    def _breakfast_button_on_click(self, e):
        self.breakfast_progress_ring_ref.current.visible = True
        self.breakfast_button_ref.current.disabled = True
        self.lunch_button_ref.current.disabled = True
        self.update()
        self.on_meal_select(self.currently_showing_employee, Meal.BREAKFAST)

    def _lunch_button_on_click(self, e):
        self.lunch_progress_ring_ref.current.visible = True
        self.breakfast_button_ref.current.disabled = True
        self.lunch_button_ref.current.disabled = True
        self.update()
        self.on_meal_select(self.currently_showing_employee, Meal.LUNCH)

    def update_frame_image(self, image_base64):
        if self.is_mounted is False:
            return
        if self.frame_image_ref.current is not None and image_base64 is not None:
            self.frame_image_ref.current.src_base64 = image_base64
            self.update()

    def show_meal_info(self, employee_info: Employee):
        self.currently_showing_employee = employee_info
        self.meal_info_timestamp = time.time()

        is_breakfast_disabled = True
        is_lunch_disabled = True

        booked_meals = [] if employee_info.booked_meals is None else employee_info.booked_meals
        for booked_meal in booked_meals:
            if booked_meal == Meal.BREAKFAST:
                is_breakfast_disabled = employee_info.has_consumed(
                    meal=Meal.BREAKFAST)
            elif booked_meal == Meal.LUNCH:
                is_lunch_disabled = employee_info.has_consumed(
                    meal=Meal.LUNCH)
        self.meal_info_container_ref.current.bgcolor = flet.colors.ON_SECONDARY
        self.meal_info_container_ref.current.content = self._get_meal_info_control(
            employee_name=employee_info.name,
            is_breakfast_disable=is_breakfast_disabled,
            is_lunch_disable=is_lunch_disabled
        )
        self.update()

    def show_booking_not_found_info(self, employee_id: str):
        self.meal_info_timestamp = time.time()
        self.meal_info_container_ref.current.bgcolor = flet.colors.ERROR_CONTAINER
        self.meal_info_container_ref.current.content = self._get_booking_not_found_control(
            employee_id=employee_id,)
        self.update()

    def _hide_meal_info(self, tick=None):
        if self.meal_info_timestamp is None:
            return

        # Calculate the difference in seconds
        diff_seconds = time.time() - self.meal_info_timestamp
        if diff_seconds > 10:
            self.meal_info_container_ref.current.bgcolor = flet.colors.ON_SECONDARY
            self.meal_info_container_ref.current.content = self._get_description_control()
            self.update()
            self.currently_showing_employee = None

    def handle_meal_submission_result(self):
        self.meal_info_timestamp = None
        self.meal_info_container_ref.current.bgcolor = flet.colors.ON_SECONDARY
        self.meal_info_container_ref.current.content = self._get_description_control()
        self.update()
        self.currently_showing_employee = None

    def _start_meal_info_timmer(self):
        self.meal_info_observable = rx.interval(1.0)
        self.meal_info_subscription = self.meal_info_observable.subscribe(
            on_next=self._hide_meal_info)
