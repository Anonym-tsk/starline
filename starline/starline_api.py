"""Data StarLine API."""
import logging
from typing import Dict, List, Callable, Optional, Any
from .base_api import BaseApi
from .device import StarlineDevice

_LOGGER = logging.getLogger(__name__)


class StarlineApi(BaseApi):
    """Data StarLine API class."""

    def __init__(self, user_id: str, slnet_token: str):
        """Constructor."""
        super().__init__()
        self._user_id: str = user_id
        self._slnet_token: str = slnet_token
        self._devices: Dict[str, StarlineDevice] = {}
        self._available: bool = False
        self._update_listeners: List[Callable] = []

    def _call_listeners(self) -> None:
        """Call listeners for update notifications."""
        for listener in self._update_listeners:
            listener()

    def add_update_listener(self, listener: Callable) -> None:
        """Add a listener for update notifications."""
        self._update_listeners.append(listener)

    async def update(self) -> None:
        """Update StarLine data."""
        devices = await self.get_user_info()
        if not devices:
            self._available = False
        else:
            self._available = True
            for device_data in devices:
                device_id = str(device_data["device_id"])
                if device_id not in self._devices:
                    self._devices[device_id] = StarlineDevice()
                self._devices[device_id].update(device_data)

        self._call_listeners()

    @property
    def devices(self) -> Dict[str, StarlineDevice]:
        """Devices list."""
        return self._devices

    @property
    def available(self) -> bool:
        """Is data available"""
        return self._available

    async def get_user_info(self) -> Optional[List[Dict[str, Any]]]:
        """Get user information."""
        url = "https://developer.starline.ru/json/v2/user/{}/user_info".format(self._user_id)
        headers = {"Cookie": "slnet=" + self._slnet_token}
        response = await self._get(url, headers=headers)
        if response is None:
            return None

        code = int(response["code"])
        if code == 200:
            return response["devices"] + response["shared_devices"]
        return None

    async def set_car_state(self, device_id: str, name: str, state: bool):
        """Set car state information."""
        _LOGGER.debug("Setting car %s state: %s=%d", device_id, name, state)
        url = "https://developer.starline.ru/json/v1/device/{}/set_param".format(device_id)
        data = {"type": name, name: 1 if state else 0}
        headers = {"Cookie": "slnet=" + self._slnet_token}
        response = await self._post(url, json=data, headers=headers)
        if response is None:
            return None

        code = int(response["code"])
        if code == 200:
            self._devices[device_id].update_car_state(response)
            self._call_listeners()
            return response
        return None

    def set_user_id(self, user_id: str) -> None:
        """Update user ID."""
        self._user_id = user_id

    def set_slnet_token(self, slnet_token: str) -> None:
        """Update SLNet token."""
        self._slnet_token = slnet_token
