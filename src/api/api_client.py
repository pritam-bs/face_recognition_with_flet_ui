import httpx
from typing import Optional, TypeVar, Union
from pydantic import BaseModel
import rx
from rx.subject.asyncsubject import AsyncSubject
import asyncio
from logger import logger

T = TypeVar('T', bound=BaseModel)
ErrorType = Union[httpx.HTTPError, httpx.NetworkError, Exception, BaseModel]


class ErrorModel(BaseModel):
    status_code: int
    content: Optional[dict]


class APIClient:
    def __init__(self, base_url):
        self.base_url = base_url
        timeout = httpx.Timeout(10.0, connect=60.0)
        self.client = httpx.Client(timeout=timeout)
        self.method = "GET"
        self.path = ""
        self.headers = {}
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

    def set_headers(self, headers):
        self.headers = headers
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
        except Exception as error:
            subject.on_error(error)

        return subject

    def _make_request_sync(self, model_type: T) -> Union[T, ErrorType]:
        url = f"{self.base_url}/{self.path}"
        try:
            response = self.client.request(
                self.method, url, headers=self.headers, params=self.params, json=self.json)
            response.raise_for_status()  # Raise exception for non-2xx status codes
            return model_type.parse_obj(response.json())
        except httpx.InvalidURL as url_error:
            logger.error("Invaild api call")
            return url_error
        except httpx.NetworkError as network_error:
            return network_error
        except httpx.HTTPStatusError as http_error:
            return ErrorModel(status_code=http_error.response.status_code, content=http_error.response.json())
        except Exception as e:
            return e

    @classmethod
    def create(cls, base_url):
        return cls(base_url)
