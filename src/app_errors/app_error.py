from typing import Optional, Union
from pydantic import BaseModel
from enum import Enum


class ErrorModel(BaseModel):
    status_code: int
    content: Optional[dict]


class AppError(Enum):
    INVALID_INPUT = ErrorModel(status_code=1000, content={
                               "message": "Invalid input."})
    DATABASE_CONNECTION = ErrorModel(status_code=1001, content={
                                     "message": "Failed to establish a database connection."})
    FILE_NOT_FOUND = ErrorModel(status_code=1002, content={
                                "message": "File not found."})
    PERMISSION_DENIED = ErrorModel(status_code=1003, content={
                                   "message": "Permission denied."})
    API_REQUEST_FAILED = ErrorModel(status_code=1004, content={
                                    "message": "Failed to make an API request."})
    NETWORK_ERROR = ErrorModel(status_code=1005, content={
                               "message": "Network error occurred."})
    UNKNOWN_ERROR = ErrorModel(status_code=1006, content={
                               "message": "Unknown error occurred."})


class AppException(Exception):
    def __init__(self, error: ErrorModel):
        self.error = error
