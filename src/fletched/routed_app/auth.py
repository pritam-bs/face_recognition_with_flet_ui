from typing import Callable, Type

from fletched.routed_app.view_builder import ViewBuilder
from fletched.routed_app.auth_store import AuthStore


def login_required(view_builder_class: Type[ViewBuilder]) -> Type[ViewBuilder]:
    def inner(self) -> bool:
        if not AuthStore(page=self.page).get_tokens():
            return False
        return True

    view_builder_class.auth_func = inner

    return view_builder_class


def group_required(group: str) -> Callable[..., Type[ViewBuilder]]:
    def wrapper(view_builder_class: Type[ViewBuilder]) -> Type[ViewBuilder]:
        def inner(self) -> bool:
            if (
                not AuthStore(page=self.page).get_tokens()
                or group not in AuthStore(page=self.page).get_user_groups()
            ):
                return False
            return True

        view_builder_class.auth_func = inner
        return view_builder_class

    return wrapper
