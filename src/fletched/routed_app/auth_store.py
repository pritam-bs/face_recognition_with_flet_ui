import flet
from flet.security import encrypt, decrypt
from fletched.routed_app.auth_store_settings import auth_store_settings
from typing import List


class AuthStore:
    access_token_key = "ACCESS_TOKEN_KEY"
    refresh_token_key = "REFRESH_TOKEN_KEY"
    user_group_key = "USER_GROUP_KEY"

    def __init__(self, page: flet.Page):
        self.page = page

    def save_tokens(self, access_token: str, refresh_token: str):
        secret_key = auth_store_settings.secret_key
        encrypted_access_token = encrypt(access_token, secret_key)
        encrypted_refresh_token = encrypt(refresh_token, secret_key)
        self.page.client_storage.set(
            self.access_token_key, encrypted_access_token)
        self.page.client_storage.set(
            self.refresh_token_key, encrypted_refresh_token)

    def get_tokens(self):
        secret_key = auth_store_settings.secret_key
        encrypted_access_token = self.page.client_storage.get(
            self.access_token_key)
        encrypted_refresh_token = self.page.client_storage.get(
            self.refresh_token_key)
        access_token = decrypt(encrypted_access_token, secret_key)
        refresh_token = decrypt(encrypted_refresh_token, secret_key)

        return access_token, refresh_token

    def save_user_groups(self, groups: List[str]):
        self.page.client_storage.set(self.user_group_key, groups)

    def get_user_groups(self):
        return self.page.client_storage.get(self.user_group_key)
