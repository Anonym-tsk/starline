"""Base StarLine API."""
import aiohttp
import logging
from .const import DEFAULT_CONNECT_TIMEOUT, DEFAULT_TOTAL_TIMEOUT, DEFAULT_ENCODING, GET, POST

_LOGGER = logging.getLogger(__name__)


class BaseApi:
    """Base StarLine API class."""

    def __init__(self):
        """Constructor."""
        self._session: aiohttp.ClientSession = aiohttp.ClientSession()
        self._total_timeout: int = DEFAULT_TOTAL_TIMEOUT
        self._connect_timeout: int = DEFAULT_CONNECT_TIMEOUT
        self._encoding: str = DEFAULT_ENCODING

    def set_timeout(self, total_timeout: int, connect_timeout: int = None) -> None:
        self._total_timeout = total_timeout
        if connect_timeout is not None:
            self._connect_timeout = connect_timeout

    def set_encoding(self, encoding: str) -> None:
        self._encoding = encoding

    async def _request(
        self,
        method: str,
        url: str,
        params: dict = None,
        data: dict = None,
        json: dict = None,
        headers: dict = None,
    ) -> aiohttp.ClientResponse:
        """Make request."""

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

        # TODO: Handle Exceptions
        return response

    async def get(self, url: str, params: dict = None, headers: dict = None) -> dict:
        """Make GET request."""

        response = await self._request(GET, url, params=params, headers=headers)
        data = await response.json(content_type=None)
        _LOGGER.debug("  Data: {}".format(data))
        return data

    async def post(
        self,
        url: str,
        params: dict = None,
        data: dict = None,
        json: dict = None,
        headers: dict = None,
    ) -> dict:
        """Make POST request."""

        response = await self._request(
            POST, url, params=params, data=data, json=json, headers=headers
        )
        data = await response.json(content_type=None)
        _LOGGER.debug("  Data: {}".format(data))
        return data
