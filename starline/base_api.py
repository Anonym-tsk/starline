"""Base StarLine API."""
import aiohttp
import logging
import re
from datetime import datetime
from typing import Optional
from .const import DEFAULT_CONNECT_TIMEOUT, DEFAULT_TOTAL_TIMEOUT, DEFAULT_ENCODING, GET, POST

_LOGGER = logging.getLogger(__name__)


class BaseApi:
    """Base StarLine API class."""

    def __init__(self):
        """Constructor."""
        self._connector = aiohttp.TCPConnector(use_dns_cache=True, ttl_dns_cache=10, enable_cleanup_closed=True, force_close=True)
        self._session: aiohttp.ClientSession = aiohttp.ClientSession(connector=self._connector)
        self._total_timeout: int = DEFAULT_TOTAL_TIMEOUT
        self._connect_timeout: int = DEFAULT_CONNECT_TIMEOUT
        self._encoding: str = DEFAULT_ENCODING

    def set_timeout(self, total_timeout: int, connect_timeout: int = None) -> None:
        """Set connection timeouts."""
        self._total_timeout = total_timeout
        if connect_timeout is not None:
            self._connect_timeout = connect_timeout

    def set_encoding(self, encoding: str) -> None:
        """Set response encoding."""
        self._encoding = encoding

    async def _request(self, method: str, url: str, params: dict = None, data: dict = None, json: dict = None, headers: dict = None) -> Optional[aiohttp.ClientResponse]:
        """Make request."""

        try:
            response = await self._session.request(
                method,
                url,
                params=params,
                data=data,
                json=json,
                headers=headers,
                timeout=aiohttp.ClientTimeout(
                    total=self._total_timeout,
                    connect=self._connect_timeout
                ),
            )
            response.raise_for_status()
            response.encoding = self._encoding

            _LOGGER.debug("StarlineApi {} request: {}".format(method, url))
            _LOGGER.debug("  Payload: {}".format(params))
            _LOGGER.debug("  Data: {}".format(data))
            _LOGGER.debug("  JSON: {}".format(json))
            _LOGGER.debug("  Headers: {}".format(headers))
            _LOGGER.debug("  Response: {}".format(response))

            return response
        except aiohttp.ClientError as error:
            _LOGGER.error("Request failed: %s", error)
            return None

    async def _get(self, url: str, params: dict = None, headers: dict = None) -> Optional[dict]:
        """Make GET request."""

        response = await self._request(GET, url, params=params, headers=headers)
        if response is None:
            return None

        data = await response.json(content_type=None)
        _LOGGER.debug("  Data: {}".format(data))
        return data

    async def _post(self, url: str, params: dict = None, data: dict = None, json: dict = None, headers: dict = None) -> Optional[dict]:
        """Make POST request."""

        response = await self._request(POST, url, params=params, data=data, json=json, headers=headers)
        if response is None:
            return None

        data = await response.json(content_type=None)
        _LOGGER.debug("  Data: {}".format(data))
        return data

    async def get_user_id(self, slid_token: str) -> (str, float, str):
        """Authenticate user by StarLineID token."""

        url = "https://developer.starline.ru/json/v2/auth.slid"
        data = {"slid_token": slid_token}
        response = await self._request(POST, url, json=data)
        if response is None:
            raise Exception("Failed to get SLNet token")

        json = await response.json(content_type=None)
        if int(json["code"]) != 200:
            raise Exception(json["codestring"])

        # Read cookie from headers because of bug https://gitlab.com/starline/openapi/issues/3
        cookie_header = response.headers.get("Set-Cookie")
        slnet = re.search("slnet=([^;]+);", cookie_header)
        expires = re.search("expires=([^;]+);", cookie_header)

        if slnet is None:
            raise Exception("Failed to get SLNet token")

        slnet_token = slnet.group(1)
        expires_time = datetime.now().timestamp() + (4 * 60 * 60)  # Now + 4h

        if expires is not None:
            try:
                expires_time = datetime.strptime(expires.group(1), '%A, %d-%b-%y %H:%M:%S %Z').timestamp()
            except:
                pass

        _LOGGER.debug("SLNet token: {}".format(slnet_token))
        return slnet_token, expires_time, json["user_id"]
