from settings import settings
import logging

# Set the logging configuration based on the environment
if settings.log_level == "DEBUG":
    # Development environment logging configuration
    logging.getLogger().setLevel(logging.DEBUG)
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
elif settings.log_level == "INFO":
    # Production environment logging configuration
    logging.getLogger().setLevel(logging.INFO)
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s')
else:
    raise ValueError("Invalid environment specified")

# Create a logger instance
logger = logging.getLogger(__name__)
