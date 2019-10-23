"""Base StarLine API."""
import logging
import requests
from datetime import datetime
from typing import Optional
from .const import DEFAULT_CONNECT_TIMEOUT, DEFAULT_READ_TIMEOUT, DEFAULT_ENCODING, GET, POST

_LOGGER = logging.getLogger(__name__)


class BaseApi:
    """Base StarLine API class."""

    def __init__(self):
        """Constructor."""
        self._session: requests.Session = requests.Session()
        self._connect_timeout: int = DEFAULT_CONNECT_TIMEOUT
        self._read_timeout: int = DEFAULT_READ_TIMEOUT
        self._encoding: str = DEFAULT_ENCODING

    def set_timeout(self, read_timeout: int, connect_timeout: int = None) -> None:
        """Set connection timeouts."""
        self._read_timeout = read_timeout
        if connect_timeout is not None:
            self._connect_timeout = connect_timeout

    def set_encoding(self, encoding: str) -> None:
        """Set response encoding."""
        self._encoding = encoding

    def _request(self, method: str, url: str, params: dict = None, data: dict = None, json: dict = None, headers: dict = None) -> Optional[requests.Response]:
        """Make request."""

        try:
            response = self._session.request(
                method,
                url,
                params=params,
                data=data,
                json=json,
                headers=headers,
                timeout=(self._connect_timeout, self._read_timeout),
            )
            response.encoding = self._encoding
            response.raise_for_status()

            _LOGGER.debug("StarlineApi {} request: {}".format(method, url))
            _LOGGER.debug("  Payload: {}".format(params))
            _LOGGER.debug("  Data: {}".format(data))
            _LOGGER.debug("  JSON: {}".format(json))
            _LOGGER.debug("  Headers: {}".format(headers))
            _LOGGER.debug("  Response: {}".format(response))

            return response
        except requests.exceptions.RequestException as error:
            _LOGGER.error("Request failed: %s", error)
            return None

    def _get(self, url: str, params: dict = None, headers: dict = None) -> Optional[dict]:
        """Make GET request."""

        response = self._request(GET, url, params=params, headers=headers)
        if response is None:
            return None

        data = response.json()
        _LOGGER.debug("  Data: {}".format(data))
        return data

    def _post(self, url: str, params: dict = None, data: dict = None, json: dict = None, headers: dict = None) -> Optional[dict]:
        """Make POST request."""

        response = self._request(POST, url, params=params, data=data, json=json, headers=headers)
        if response is None:
            return None

        data = response.json()
        _LOGGER.debug("  Data: {}".format(data))
        return data

    def get_user_id(self, slid_token: str) -> (str, float, str):
        """Authenticate user by StarLineID token."""

        url = "https://developer.starline.ru/json/v2/auth.slid"
        data = {"slid_token": slid_token}
        response = self._request(POST, url, json=data)
        if response is None:
            raise Exception("Failed to get SLNet token")

        json = response.json()
        if int(json["code"]) != 200:
            raise Exception(json["codestring"])

        slnet_token = None
        expires_time = datetime.now().timestamp() + (4 * 60 * 60)  # Now + 4h
        for cookie in response.cookies:
            if cookie.name == 'slnet':
                slnet_token = cookie.value
                if cookie.expires:
                    expires_time = cookie.expires

        if slnet_token is None:
            raise Exception("Failed to get SLNet token")

        _LOGGER.debug("SLNet token: {}".format(slnet_token))
        return slnet_token, expires_time, json["user_id"]
