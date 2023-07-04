import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env', env_file_encoding='utf-8', extra="ignore")
    auth_client: str = Field(alias="AUTH_CLIENT_ID")
    auth_client_secret: str = Field(alias="AUTH_CLIENT_SECRET")
    auth_uri: str = Field(alias="AUTH_URI")
    token_uri: str = Field(alias="TOKEN_URI")
    project_id: str = Field(alias="PROJECT_ID")
    log_level: str = Field(alias="LOG_LEVEL")
    opm_base_url: str = Field(alias="OPM_BASE_URL")


# Determine the environment dynamically
# Load environment variables from .env file
load_dotenv()
# Set the desired environment (e.g., dev, prod, etc.)
environment = os.getenv("APP_ENV")

# Set the environment file based on the chosen environment
settings = None
if environment == "dev":
    # Create an instance of Settings for dev
    settings = Settings(
        _env_file='dev.env', _env_file_encoding='utf-8')
elif environment == "prod":
    # Create an instance of Settings for prod
    settings = Settings(
        _env_file='prod.env', _env_file_encoding='utf-8')
else:
    raise ValueError("Invalid environment specified")
