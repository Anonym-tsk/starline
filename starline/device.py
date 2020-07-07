"""StarLine device."""
from typing import Optional, Dict, Any, List
from .const import (
    BATTERY_LEVEL_MIN,
    BATTERY_LEVEL_MAX,
    GSM_LEVEL_MIN,
    GSM_LEVEL_MAX,
    DEVICE_FUNCTION_POSITION,
    DEVICE_FUNCTION_STATE,
)


class StarlineDevice:
    """StarLine device class."""

    def __init__(self):
        """Constructor."""
        self._device_id: Optional[str] = None
        self._imei: Optional[str] = None
        self._alias: Optional[str] = None
        self._battery: Optional[int] = None
        self._ctemp: Optional[int] = None
        self._etemp: Optional[int] = None
        self._fw_version: Optional[str] = None
        self._gsm_lvl: Optional[int] = None
        self._phone: Optional[str] = None
        self._status: Optional[int] = None
        self._ts_activity: Optional[float] = None
        self._typename: Optional[str] = None
        self._balance: Dict[str, Dict[str, Any]] = {}
        self._car_state: Dict[str, bool] = {}
        self._car_alr_state: Dict[str, bool] = {}
        self._functions: List[str] = []
        self._position: Dict[str, float] = {}
        self._fuel: Dict[str, Any] = {}
        self._errors: Dict[str, Any] = {}
        self._mileage: Dict[str, Any] = {}

    def update(self, device_data):
        """Update data from server."""
        self._device_id = str(device_data.get("device_id"))
        self._imei = device_data.get("imei")
        self._alias = device_data.get("alias")
        self._battery = device_data.get("battery")
        self._ctemp = device_data.get("ctemp", device_data.get("mayak_temp"))
        self._etemp = device_data.get("etemp")
        self._fw_version = device_data.get("fw_version")
        self._gsm_lvl = device_data.get("gsm_lvl")
        self._phone = device_data.get("phone")
        self._status = device_data.get("status")
        self._ts_activity = device_data.get("ts_activity")
        self._typename = device_data.get("typename")
        self._balance = device_data.get("balance", {})
        self._car_state = device_data.get("car_state", {})
        self._car_alr_state = device_data.get("car_alr_state", {})
        self._functions = device_data.get("functions", [])
        self._position = device_data.get("position")

    def update_obd(self, obd_info):
        """Update OBD data from server."""
        self._fuel = obd_info.get("fuel")
        self._errors = obd_info.get("errors")
        self._mileage = obd_info.get("mileage")

    def update_car_state(self, car_state):
        """Update car state from server."""
        for key in car_state:
            if key in self._car_state:
                self._car_state[key] = car_state[key] in ["1", "true", True]

    @property
    def support_position(self):
        """Is position supported by this device."""
        return DEVICE_FUNCTION_POSITION in self._functions and self._position

    @property
    def support_state(self):
        """Is state supported by this device."""
        return DEVICE_FUNCTION_STATE in self._functions and self._car_state

    @property
    def device_id(self):
        """Device ID."""
        return self._device_id

    @property
    def fw_version(self):
        """Firmware version."""
        return self._fw_version

    @property
    def name(self):
        """Device name."""
        return self._alias

    @property
    def typename(self):
        """Device type name."""
        return self._typename

    @property
    def position(self):
        """Car position."""
        return self._position

    @property
    def online(self):
        """Is device online."""
        return int(self._status) == 1

    @property
    def battery_level(self):
        """Car battery level."""
        return self._battery

    @property
    def battery_level_percent(self):
        """Car battery level percent."""
        if self._battery is None:
            return 0
        if self._battery > BATTERY_LEVEL_MAX:
            return 100
        if self._battery < BATTERY_LEVEL_MIN:
            return 0
        return round(
            (self._battery - BATTERY_LEVEL_MIN)
            / (BATTERY_LEVEL_MAX - BATTERY_LEVEL_MIN)
            * 100
        )

    @property
    def balance(self):
        """Device balance."""
        return self._balance.get("active", {})

    @property
    def car_state(self):
        """Car state."""
        return self._car_state

    @property
    def alarm_state(self):
        """Car alarm level."""
        return self._car_alr_state

    @property
    def temp_inner(self):
        """Car inner temperature."""
        return self._ctemp

    @property
    def temp_engine(self):
        """Engine temperarure."""
        return self._etemp

    @property
    def gsm_level(self):
        """GSM signal level."""
        if self._gsm_lvl is None:
            return None
        if not self.online:
            return 0
        return self._gsm_lvl

    @property
    def gsm_level_percent(self):
        """GSM signal level percent."""
        if self.gsm_level is None:
            return None
        if self.gsm_level > GSM_LEVEL_MAX:
            return 100
        if self.gsm_level < GSM_LEVEL_MIN:
            return 0
        return round(
            (self.gsm_level - GSM_LEVEL_MIN) / (GSM_LEVEL_MAX - GSM_LEVEL_MIN) * 100
        )

    @property
    def imei(self):
        """Device IMEI."""
        return self._imei

    @property
    def phone(self):
        """Device phone number."""
        return self._phone

    @property
    def fuel(self):
        """Device fuel count."""
        return self._fuel

    @property
    def errors(self):
        """Device errors info."""
        return self._errors

    @property
    def mileage(self):
        """Device mileage count."""
        return self._mileage
