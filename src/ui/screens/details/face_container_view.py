import flet
from ui.screens.details.employee import Employee
from typing import Protocol
from typing import Callable
from ui.screens.details.employee import Meal
from typing import Optional
from flet_core.ref import Ref


class FaceContainerProtocol(Protocol):
    def on_meal_select(meal: Meal):
        ...


class FaceContainerView(flet.UserControl, FaceContainerProtocol):
    MealSelectCallable = Callable[[any, Meal], None]

    def __init__(self, on_meal_select: MealSelectCallable, ref: Optional[Ref]):
        super().__init__(ref=ref)
        self.breakfast_progress_ring_ref = flet.Ref[flet.ProgressRing]()
        self.lunch_progress_ring_ref = flet.Ref[flet.ProgressRing]()
        self.breakfast_button_ref = flet.Ref[flet.ElevatedButton]()
        self.lunch_button_ref = flet.Ref[flet.ElevatedButton]()
        self.on_meal_select = on_meal_select
        self.frame_image_ref = flet.Ref[flet.Image]()

    def build(self):
        return flet.Column(
            controls=[
                flet.Text("Scan your face",
                          style=flet.TextThemeStyle.TITLE_LARGE),
                flet.Image(
                    ref=self.frame_image_ref,
                    src_base64=None,
                    width=200,
                    height=200,
                    fit=flet.ImageFit.COVER,
                ),
                flet.Text("Hello Name of the employee",
                          style=flet.TextThemeStyle.TITLE_MEDIUM),
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
                    alignment=flet.MainAxisAlignment.CENTER,
                    vertical_alignment=flet.CrossAxisAlignment.CENTER,
                )

            ],
            alignment=flet.MainAxisAlignment.CENTER,
            horizontal_alignment=flet.CrossAxisAlignment.CENTER,
        )

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
        if self.frame_image_ref.current is not None:
            self.frame_image_ref.current.src_base64 = image_base64
            self.update()
