import os
from dotenv import load_dotenv
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    auth_client: str = Field(env="AUTH_CLIENT_ID")
    auth_client_secret: str = Field(env="AUTH_CLIENT_SECRET")
    auth_uri: str = Field(env="AUTH_URI")
    token_uri: str = Field(env="TOKEN_URI")
    project_id: str = Field(env="PROJECT_ID")
    log_level: str = Field(env="LOG_LEVEL")

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
    Settings.Config.env_file = "dev.env"
elif environment == "prod":
    Settings.Config.env_file = "prod.env"
else:
    raise ValueError("Invalid environment specified")


# Create an instance of AppSettings
settings = Settings()
