import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class AuthStoreSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env', env_file_encoding='utf-8', extra="ignore")
    secret_key: str = Field(alias="AUTH_STORE_SECRET_KEY")


# Determine the environment dynamically
# Load environment variables from .env file
load_dotenv()
# Set the desired environment (e.g., dev, prod, etc.)
environment = os.getenv("APP_ENV")

# Set the environment file based on the chosen environment
auth_store_settings = None
if environment == "dev":
    # Create an instance of AuthStoreSettings for dev
    auth_store_settings = AuthStoreSettings(
        _env_file='dev.env', _env_file_encoding='utf-8')
elif environment == "prod":
    # Create an instance of AuthStoreSettings for prod
    auth_store_settings = AuthStoreSettings(
        _env_file='prod.env', _env_file_encoding='utf-8')
else:
    raise ValueError("Invalid environment specified")
