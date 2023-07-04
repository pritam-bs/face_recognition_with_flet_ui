import httpx
from rx.subject.asyncsubject import AsyncSubject
from app_errors.app_error import AppError, ErrorModel, AppException
from typing import TypeVar, Union, List
from pydantic import BaseModel, TypeAdapter
from logger import logger
import json
import html2text

T = TypeVar('T', bound=Union[BaseModel, List[BaseModel]])


class APIClient:
    def __init__(self, base_url):
        self.base_url = base_url
        timeout = httpx.Timeout(10.0, connect=60.0)
        self.client = httpx.Client(timeout=timeout)
        self.method = "GET"
        self.path = ""
        self.headers = {"Content-Type": "application/json"}
        self.params = {}
        self.json = None

    async def close(self):
        await self.client.aclose()

    def get(self):
        self.method = "GET"
        return self

    def post(self):
        self.method = "POST"
        return self

    def set_path(self, path):
        self.path = path
        return self

    def add_headers(self, headers):
        self.headers.update(headers)
        return self

    def set_params(self, params):
        self.params = params
        return self

    def set_json(self, json_data):
        self.json = json_data
        return self

    def make_request(self, model_type: T) -> AsyncSubject:
        subject = AsyncSubject()
        try:
            result = self._make_request_sync(model_type=model_type)
            subject.on_next(result)
            subject.on_completed()
        except AppException as e:
            subject.on_error(e.error)
        except Exception as e:
            logger.debug(e)

        return subject

    def _make_request_sync(self, model_type: T) -> Union[T, ErrorModel]:
        url = f"{self.base_url}/{self.path}"
        try:
            response = self.client.request(
                self.method, url, headers=self.headers, params=self.params, json=self.json)
            response.raise_for_status()  # Raise exception for non-2xx status codes
            # return parse_raw_as(model_type, response.content)
            response_data = TypeAdapter(
                type=model_type).validate_json(response.content)
            return response_data
        except httpx.InvalidURL:
            logger.error("Invaild api call")
            raise AppException(error=AppError.INVALID_INPUT.value)
        except httpx.NetworkError:
            raise AppException(error=AppError.NETWORK_ERROR.value)
        except httpx.HTTPStatusError as http_error:
            status_code = http_error.response.status_code
            try:
                content = http_error.response.json()
            except json.JSONDecodeError:
                text_maker = html2text.HTML2Text()
                text_maker.ignore_links = True
                text_maker.bypass_tables = False
                html = http_error.response.content.decode("utf-8")
                text = text_maker.handle(data=html)
                content = {"message": text}
            error = ErrorModel(status_code=status_code, content=content)
            raise AppException(error=error)
        except Exception as e:
            raise AppException(error=AppError.UNKNOWN_ERROR.value)

    @classmethod
    def create(cls, base_url):
        return cls(base_url)
