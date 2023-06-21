import pydantic
from enum import Enum
from typing import List
from pydantic import BaseModel


class Meal(Enum):
    BREAKFAST = "Breafast"
    LUNCH = "Lunch"
    SNACKS = "Snacks"


class Employee(BaseModel):
    name: str
    email: str
    employeeID: str
    booked_meals: List[Meal] | None
    isEmergency: bool
    consumed_meals: List[Meal] | None

    def has_consumed(self, meal: Meal) -> bool:
        return self.consumed_meals and meal in self.consumed_meals
