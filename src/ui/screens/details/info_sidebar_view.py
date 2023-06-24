import flet
from typing import List
from ui.screens.details.employee import Employee
from ui.screens.details.employee import Meal
from ui.screens.details.employee_list_item_view import EmployeeListItemView
from ui.screens.details.employees import employees


class InfoSidebarView(flet.UserControl):
    def __init__(self):
        super().__init__()
        self.list_view = flet.ListView(
            expand=True,
            width=300,
            spacing=5,
            padding=10
        )
        self.total_booked_breakfast_ref = flet.Ref[flet.Text]()
        self.total_booked_lunch_ref = flet.Ref[flet.Text]()
        self.total_emergency_booked_ref = flet.Ref[flet.Text]()

    def did_mount(self):
        self.update_list(employee_list=employees)

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
                self.list_view,
            ],
            alignment=flet.MainAxisAlignment.START,
            horizontal_alignment=flet.CrossAxisAlignment.START,
        )

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
            employee.isEmergency for employee in employee_list)

        self.total_booked_breakfast_ref.current.value = f"Total Breakfast: {total_booked_breakfast_count}"
        self.total_booked_lunch_ref.current.value = f"Total Lunch: {total_booked_lunch_count}"
        self.total_emergency_booked_ref.current.value = f"Emergency Count: {total_emergency_count}"

        self.update()
