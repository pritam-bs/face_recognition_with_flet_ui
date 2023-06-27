import flet
from data_models.employee import Employee


class EmployeeListItemView(flet.UserControl):
    def __init__(self, employee: Employee):
        super().__init__()
        self.employee = employee

    def build(self):
        meal_row = flet.Row()
        if self.employee.booked_meals is not None and len(self.employee.booked_meals) > 0:
            for booked_meal in self.employee.booked_meals:
                bgcolor = flet.colors.TRANSPARENT
                if self.employee.has_consumed(meal=booked_meal):
                    bgcolor = flet.colors.GREEN
                meal = flet.Container(
                    content=flet.Text(booked_meal.value,
                                      style=flet.TextThemeStyle.LABEL_MEDIUM),
                    border=flet.border.all(
                        width=1, color=flet.colors.GREEN),
                    padding=4,
                    border_radius=4,
                    bgcolor=bgcolor,
                )
                meal_row.controls.append(meal)
        else:
            meal_row.visible = False

        return flet.Card(
            content=flet.Container(
                content=flet.Column(
                    controls=[
                        flet.Text(self.employee.name),
                        meal_row,
                    ],
                    alignment=flet.MainAxisAlignment.CENTER,
                ),
                padding=10,
                alignment=flet.alignment.center_left
            ),
        )
