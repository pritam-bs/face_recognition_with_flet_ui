from oauthlib.oauth2.rfc8628.clients.device import DeviceClient
import httpx
from httpx import Response
from settings import settings
import json
from logger import logger
from pydantic import BaseModel


class DiscoveryDocument(BaseModel):
    device_authorization_endpoint: str
    token_endpoint: str


class AuthorizationResponse(BaseModel):
    device_code: str
    user_code: str
    verification_url: str
    expires_in: int
    interval: int


class TokenResponse(BaseModel):
    access_token: str
    expires_in: int
    scope: str
    token_type: str
    refresh_token: str


class OAuthClient:
    discovery_document_url = "https://accounts.google.com/.well-known/openid-configuration"
    client_id = settings.auth_client
    client_secret = settings.auth_client_secret
    scopes = [
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
    ]
    kwargs = {'client_secret': client_secret}
    discovery_document = None

    device_client = DeviceClient(
        client_id=client_id, scope=scopes, kwargs=kwargs)
    timeout = httpx.Timeout(10.0, connect=60.0)
    api_client = httpx.Client(timeout=timeout)

    def _get_discovery_document(self):
        if self.discovery_document is not None:
            return self.discovery_document
        try:
            response: Response = self.api_client.request(
                method="GET", url=self.discovery_document_url)
            response.raise_for_status()

            self.discovery_document = DiscoveryDocument.parse_obj(
                response.json())
            return self.discovery_document
        except Exception as e:
            return e

    def request_codes(self):
        try:
            discovery_document = self._get_discovery_document()
            if discovery_document.device_authorization_endpoint is None:
                logger.debug("device_authorization_endpoint not found")
                return
            request_url = self.device_client.prepare_request_uri(
                uri=discovery_document.device_authorization_endpoint, scope=self.scopes)
            response: Response = self.api_client.request(
                url=request_url, method="POST")
            response.raise_for_status()
            self.authorization_response = AuthorizationResponse.parse_obj(
                response.json())
            return self.authorization_response
        except Exception as e:
            pass

    def request_token(self):
        try:
            request_body = self.device_client.prepare_request_body(
                device_code=self.authorization_response.device_code, include_client_id=True, kwargs=self.kwargs)
            response: Response = self.api_client.request(
                url=self.discovery_document.token_endpoint, method="POST", data=request_body)
            token = TokenResponse.parse_obj(response.json())
            self._send_token(token=token.access_token)
        except Exception as e:
            pass

    def _send_token(self, token: str):
        logger.debug(token)
