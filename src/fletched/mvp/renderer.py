import flet as ft
from pydantic import BaseModel

from fletched.mvp.error import ErrorMessage
from typing import Dict


class MvpRenderer:
    def __init__(self, ref_map: Dict[str, ft.Ref]) -> None:
        self.ref_map = ref_map

    def render(self, model: BaseModel) -> None:
        model_map = model.dict()

        for variable_name, ref in self.ref_map.items():
            model_field_content = model_map[variable_name]

            if hasattr(ref.current, "value"):
                control_attribute_name = "value"
                control_attribute_content = getattr(
                    ref.current, control_attribute_name)
                if model_field_content == control_attribute_content:
                    continue
                setattr(ref.current, control_attribute_name,
                        model_field_content)
            elif hasattr(ref.current, "text"):
                control_attribute_name = "text"
                control_attribute_content = getattr(
                    ref.current, control_attribute_name)
                if model_field_content == control_attribute_content:
                    continue
                setattr(ref.current, control_attribute_name,
                        model_field_content)

            if isinstance(model_field_content, ErrorMessage):
                control_attribute_name = "error_text"
                model_field_content = model_field_content.message
                control_attribute_content = getattr(
                    ref.current, control_attribute_name)
                if model_field_content == control_attribute_content:
                    continue
                setattr(ref.current, control_attribute_name,
                        model_field_content)
