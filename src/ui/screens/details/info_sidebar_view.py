import flet
from typing import List
from data_models.employee import Employee, Meal
from ui.screens.details.employee_list_item_view import EmployeeListItemView
from ui.screens.details.details_presenter import DetailsPresenterProtocol
from typing import Optional
from flet_core.ref import Ref
from logger import logger
from rx.subject import Subject
from rx.operators import distinct_until_changed
from enum import Enum


class ScrollBehavior(Enum):
    PULL_TO_REFRESH = 1
    PAGINATION = 2
    SCROLL = 3


class InfoSidebarView(flet.UserControl):
    def __init__(self, presenter: DetailsPresenterProtocol, ref: Optional[Ref]):
        super().__init__(ref=ref)
        self.presenter = presenter
        self.list_view = flet.ListView(
            on_scroll=self._on_scroll,
            expand=True,
            width=300,
            spacing=5,
            padding=10
        )
        self.total_booked_breakfast_ref = flet.Ref[flet.Text]()
        self.total_booked_lunch_ref = flet.Ref[flet.Text]()
        self.total_emergency_booked_ref = flet.Ref[flet.Text]()
        self.update_progress_ref = flet.Ref[flet.Container]()
        self.refresh_view_ref = flet.Ref[flet.Container]()

    def did_mount(self):
        self.presenter.get_employees()
        self._config_scroll_behavior()

    def will_unmount(self):
        self.subscription.dispose()

    def build(self):
        return flet.Column(
            controls=[
                flet.Card(
                    flet.Container(
                        content=flet.Column(
                            controls=[
                                flet.Text(ref=self.total_booked_breakfast_ref,
                                          value="Total Breakfast: 0"),
                                flet.Text(ref=self.total_booked_lunch_ref,
                                          value="Total Lunch: 0"),
                                flet.Text(ref=self.total_emergency_booked_ref,
                                          value="Emergency Count: 0"),
                            ],
                            alignment=flet.MainAxisAlignment.START,
                            horizontal_alignment=flet.CrossAxisAlignment.START,
                        ),
                        padding=10,
                    ),
                    expand=False,
                    width=300,
                ),
                flet.Stack(controls=[
                    self.list_view,
                    flet.Container(
                        ref=self.refresh_view_ref,
                        content=flet.ElevatedButton(
                            text="Refresh",
                            on_click=self._on_refresh_button_pressed,
                        ),
                        alignment=flet.alignment.bottom_center,
                    ),
                    flet.Container(
                        ref=self.update_progress_ref,
                        content=flet.ProgressRing(
                            width=30,
                            height=30,
                        ),
                        alignment=flet.alignment.center,
                        bgcolor=flet.colors.with_opacity(
                            opacity=0.4, color=flet.colors.GREY_900),
                    ),

                ],
                    width=300,
                    expand=True,
                ),
            ],
            alignment=flet.MainAxisAlignment.CENTER,
            horizontal_alignment=flet.CrossAxisAlignment.CENTER,
            expand=True,
        )

    def _on_scroll(self, event: flet.OnScrollEvent):
        pixels = event.pixels
        max_scroll_extent = event.max_scroll_extent
        min_scroll_extent = event.min_scroll_extent

        if (min_scroll_extent - pixels) > 100:
            self.scroll_behavior_subject.on_next(
                ScrollBehavior.PULL_TO_REFRESH)
        elif (pixels - max_scroll_extent) > 100:
            self.scroll_behavior_subject.on_next(ScrollBehavior.PAGINATION)
        else:
            self.scroll_behavior_subject.on_next(ScrollBehavior.SCROLL)

    def _config_scroll_behavior(self):
        def on_next(scroll_behavior):
            logger.debug(scroll_behavior)
            if scroll_behavior == ScrollBehavior.PULL_TO_REFRESH:
                self.presenter.get_employees()

        def on_error(error):
            logger.debug(error)

        def on_completed():
            logger.debug("on_completed")

        self.scroll_behavior_subject = Subject()
        self.subscription = self.scroll_behavior_subject.pipe(
            distinct_until_changed()).subscribe(
            on_next=on_next, on_error=on_error, on_completed=on_completed)

    def _on_refresh_button_pressed(self, e):
        self.presenter.get_employees()

    def update_list(self, employee_list: List[Employee]):
        self.list_view.controls.clear()
        for employee in employee_list:
            self.list_view.controls.append(
                EmployeeListItemView(employee=employee)
            )
        total_booked_breakfast_count = len(
            [employee for employee in employee_list if employee.booked_meals and Meal.BREAKFAST in employee.booked_meals])
        total_booked_lunch_count = len(
            [employee for employee in employee_list if employee.booked_meals and Meal.LUNCH in employee.booked_meals])
        total_emergency_count = sum(
            employee.is_emergency for employee in employee_list)

        self.total_booked_breakfast_ref.current.value = f"Total Breakfast: {total_booked_breakfast_count}"
        self.total_booked_lunch_ref.current.value = f"Total Lunch: {total_booked_lunch_count}"
        self.total_emergency_booked_ref.current.value = f"Emergency Count: {total_emergency_count}"

        self._update_refresh_view()

        self.update()

    def update_progress_view(self, is_in_progress: bool):
        self.update_progress_ref.current.visible = is_in_progress
        self.update()

    def _update_refresh_view(self):
        if len(self.list_view.controls) < 1:
            self.refresh_view_ref.current.visible = True
        else:
            self.refresh_view_ref.current.visible = False
