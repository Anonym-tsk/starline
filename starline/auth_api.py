"""Auth StarLine API."""
import hashlib
import logging
from .base_api import BaseApi

_LOGGER = logging.getLogger(__name__)


class StarlineAuth(BaseApi):
    """Auth StarLine API class."""

    async def get_app_code(self, app_id: str, app_secret: str) -> str:
        """Get application code for getting application token."""

        url = "https://id.starline.ru/apiV3/application/getCode/"
        payload = {
            "appId": app_id,
            "secret": hashlib.md5(app_secret.encode(self._encoding)).hexdigest(),
        }
        response = await self._get(url, params=payload)
        if response is None:
            raise Exception("Failed to get application code")

        if int(response["state"]) == 1:
            app_code = response["desc"]["code"]
            _LOGGER.debug("Application code: {}".format(app_code))
            return app_code

        raise Exception("Invalid response state: {}", response["state"])

    async def get_app_token(self, app_id: str, app_secret: str, app_code: str) -> str:
        """Get application token for authentication."""

        url = "https://id.starline.ru/apiV3/application/getToken/"
        payload = {
            "appId": app_id,
            "secret": hashlib.md5((app_secret + app_code).encode(self._encoding)).hexdigest(),
        }
        response = await self._get(url, params=payload)
        if response is None:
            raise Exception("Failed to get application token")

        if int(response["state"]) == 1:
            app_token = response["desc"]["token"]
            _LOGGER.debug("Application token: {}".format(app_token))
            return app_token

        raise Exception("Invalid response state: {}", response["state"])

    async def get_slid_user_token(self, app_token: str, user_login: str, user_password: str, sms_code: str = None, captcha_sid: str = None, captcha_code: str = None) -> (bool, dict):
        """Authenticate user by login, password and application token."""

        url = "https://id.starline.ru/apiV3/user/login/"
        payload = {"token": app_token}
        data = {
            "login": user_login,
            "pass": hashlib.sha1(user_password.encode(self._encoding)).hexdigest(),
        }
        if sms_code is not None:
            data["smsCode"] = sms_code
        if (captcha_sid is not None) and (captcha_code is not None):
            data["captchaSid"] = captcha_sid
            data["captchaCode"] = captcha_code
        response = await self._post(url, params=payload, data=data)
        if response is None:
            raise Exception("Failed to get user token")

        state = int(response["state"])
        if (state == 1) or (state == 2) or (state == 0 and "captchaSid" in response["desc"]) or (state == 0 and "phone" in response["desc"]):
            return state, response["desc"]

        raise Exception("Invalid response state: {}", state)
