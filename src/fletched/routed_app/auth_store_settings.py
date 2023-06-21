import os
from dotenv import load_dotenv
from pydantic import BaseSettings, Field


class AuthStoreSettings(BaseSettings):
    secret_key: str = Field(env="AUTH_STORE_SECRET_KEY")

    class Config:
        env_file: str
        env_file_encoding = "utf-8"


# Determine the environment dynamically
# Load environment variables from .env file
load_dotenv()
# Set the desired environment (e.g., dev, prod, etc.)
environment = os.getenv("APP_ENV")

# Set the environment file based on the chosen environment
if environment == "dev":
    AuthStoreSettings.Config.env_file = "dev.env"
elif environment == "prod":
    AuthStoreSettings.Config.env_file = "prod.env"
else:
    raise ValueError("Invalid environment specified")


# Create an instance of AuthStoreSettings
auth_store_settings = AuthStoreSettings()
