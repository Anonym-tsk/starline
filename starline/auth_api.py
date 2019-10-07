"""Auth StarLine API."""
import hashlib
from .base_api import BaseApi, POST, LOGGER


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
            LOGGER.debug("Application code: {}".format(app_code))
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
            LOGGER.debug("Application token: {}".format(app_token))
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

    async def get_user_id(self, slid_token: str) -> (str, str):
        """Authenticate user by StarLineID token."""

        url = "https://developer.starline.ru/json/v2/auth.slid"
        data = {"slid_token": slid_token}
        response = await self._request(POST, url, json=data)
        json = await response.json(content_type=None)

        # TODO: check response code
        slnet_token = response.cookies["slnet"]
        LOGGER.debug("SLnet token: {}".format(slnet_token))
        return slnet_token, json["user_id"]
