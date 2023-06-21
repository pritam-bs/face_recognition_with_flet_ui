import flet
from ui.screens.details.employee import Employee


class EmployeeListItemView(flet.UserControl):
    def __init__(self, employee: Employee):
        super().__init__()
        self.employee = employee

    def build(self):
        meal_row = flet.Row()
        for booked_meal in self.employee.booked_meals:
            bgcolor = flet.colors.TRANSPARENT
            if self.employee.has_consumed(meal=booked_meal):
                bgcolor = flet.colors.AMBER
            meal = flet.Container(
                content=flet.Text(booked_meal.value),
                border=flet.border.all(
                    width=1, color=flet.colors.AMBER),
                padding=4,
                border_radius=4,
                bgcolor=bgcolor,
            )
            meal_row.controls.append(meal)

        return flet.Card(
            content=flet.Container(
                content=flet.Column(
                    controls=[
                        flet.Text(self.employee.name),
                        flet.Row(
                            controls=[
                                meal_row,
                            ],
                        ),
                    ]
                ),
                padding=10,

            )
        )
