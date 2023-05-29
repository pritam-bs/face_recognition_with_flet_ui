from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Access the APP_ENV variable
app_env = os.getenv("APP_ENV")

# Determine the current environment
if app_env == "dev":
    # Development environment specific configuration
    # AUTH_CLIENT_ID=854064240867-altu19s8dm5ber5m8otadkebccc9god2.apps.googleusercontent.com
    # AUTH_CLIENT_SERRET=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
    # AUTH_URI=https://accounts.google.com/o/oauth2/auth
    # TOKEN_URI=https://oauth2.googleapis.com/token
    # PROJECT_ID=accesscontroldevice

    auth_client = os.getenv("AUTH_CLIENT_ID")
    auth_client_secret = os.getenv("AUTH_CLIENT_SECRET")
    auth_uri = os.getenv("AUTH_URI")
    token_uri = os.getenv("TOKEN_URI")
    project_id = os.getenv("PROJECT_ID")

    # Use the configuration values for development
    # ...
elif app_env == "prod":
    # Production environment specific configuration
    auth_client = os.getenv("AUTH_CLIENT_ID")
    auth_client_secret = os.getenv("AUTH_CLIENT_SECRET")
    auth_uri = os.getenv("AUTH_URI")
    token_uri = os.getenv("TOKEN_URI")
    project_id = os.getenv("PROJECT_ID")

    # Use the configuration values for production
    # ...
else:
    raise ValueError("Invalid environment specified")

# Use the configuration values common to both environments
# ...
