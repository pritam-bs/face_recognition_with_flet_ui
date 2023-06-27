from enum import Enum
from typing import List
from pydantic import BaseModel
import json


class Meal(str, Enum):
    BREAKFAST = "Breakfast"
    LUNCH = "Lunch"
    SNACKS = "Snacks"


class Employee(BaseModel):
    name: str
    email: str
    employee_id: str
    booked_meals: List[Meal] | None
    is_emergency: bool
    consumed_meals: List[Meal] | None

    def has_consumed(self, meal: Meal) -> bool:
        return self.consumed_meals and meal in self.consumed_meals


class EmployeeList(BaseModel):
    __root__: List[Employee]
