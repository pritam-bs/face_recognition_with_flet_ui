from enum import Enum
import flet
from data_models.employee import Employee
from typing import List, Dict
import json
from pydantic.json import pydantic_encoder
from pydantic import TypeAdapter


class ClientStorageKey(Enum):
    employee_list_key = "employee_list_key"


class ClientStorage:
    def __init__(self, page: flet.Page) -> None:
        self.page = page

    def save_employee_list(self, employee_list: List[Employee]):
        # Create dictionary with employee_id as key and Employee object as value
        employee_dict = {
            employee.employee_id: employee.model_dump() for employee in employee_list}

        # Convert dictionary to JSON string
        employee_dict_json = json.dumps(
            employee_dict, default=pydantic_encoder)
        self.page.client_storage.set(
            ClientStorageKey.employee_list_key.value, employee_dict_json)

    def get_employee_dict(self):
        employees_dict_json = self.page.client_storage.get(
            ClientStorageKey.employee_list_key.value)
        # Parse the JSON data into the specified type
        employees_dict = TypeAdapter(
            type=Dict[str, Employee]).validate_json(employees_dict_json)
        return employees_dict

    def clear_employee_list(self):
        self.page.client_storage.remove(ClientStorageKey.employee_list_key)
