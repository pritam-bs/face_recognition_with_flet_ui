from enum import Enum
from typing import List, Union
from pydantic import BaseModel, RootModel


class Meal(str, Enum):
    BREAKFAST = "Breakfast"
    LUNCH = "Lunch"
    SNACKS = "Snacks"


class Employee(BaseModel):
    name: str
    email: str
    employee_id: str
    booked_meals: Union[List[Meal], None] = None
    is_emergency: bool
    consumed_meals: Union[List[Meal], None] = None

    def has_consumed(self, meal: Meal) -> bool:
        return self.consumed_meals and meal in self.consumed_meals


class EmployeeList(RootModel):
    root: List[Employee]
