"""Auth StarLine API."""
import hashlib
import logging
import re
from datetime import datetime
from .base_api import BaseApi, POST

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
        response = await self.get(url, params=payload)

        if int(response["state"]) == 1:
            app_code = response["desc"]["code"]
            _LOGGER.debug("Application code: {}".format(app_code))
            return app_code
        raise Exception(response)

    async def get_app_token(self, app_id: str, app_secret: str, app_code: str) -> str:
        """Get application token for authentication."""

        url = "https://id.starline.ru/apiV3/application/getToken/"
        payload = {
            "appId": app_id,
            "secret": hashlib.md5((app_secret + app_code).encode(self._encoding)).hexdigest(),
        }
        response = await self.get(url, params=payload)

        if int(response["state"]) == 1:
            app_token = response["desc"]["token"]
            _LOGGER.debug("Application token: {}".format(app_token))
            return app_token
        raise Exception(response)

    async def get_slid_user_token(
        self,
        app_token: str,
        user_login: str,
        user_password: str,
        sms_code: str = None,
        captcha_sid: str = None,
        captcha_code: str = None,
    ) -> (bool, dict):
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
        response = await self.post(url, params=payload, data=data)

        state = int(response["state"])
        if (
            (state == 1)
            or (state == 2)
            or (state == 0 and "captchaSid" in response["desc"])
            or (state == 0 and "phone" in response["desc"])
        ):
            return state, response["desc"]
        raise Exception(response)

    async def get_user_id(self, slid_token: str) -> (str, float, str):
        """Authenticate user by StarLineID token."""
        # TODO: check response code
        # TODO: Продливать куку

        url = "https://developer.starline.ru/json/v2/auth.slid"
        data = {"slid_token": slid_token}
        response = await self._request(POST, url, json=data)
        json = await response.json(content_type=None)

        # Read cookie from headers because of bug https://gitlab.com/starline/openapi/issues/3
        cookie_header = response.headers.get("Set-Cookie")
        slnet = re.search("slnet=([^;]+);", cookie_header)
        expires = re.search("expires=([^;]+);", cookie_header)
        if slnet is None:
            raise Exception(response)

        slnet_token = slnet.group(1)
        expires_time = None

        if expires is not None:
            try:
                expires_time = datetime.strptime(expires.group(1), '%A, %d-%b-%y %H:%M:%S %Z').timestamp()
            except:
                pass

        _LOGGER.debug("SLnet token: {}".format(slnet_token))
        return slnet_token, expires_time, json["user_id"]
