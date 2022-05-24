import http.client
import json
import uuid
import webbrowser
from urllib import parse as url_encode


class Token:
    def __init__(
        self,
        token_type: str,
        scope: str,
        expires_in: int,
        access_token: str,
    ):
        self.token_type = token_type
        self.scope = scope
        self.expires_in = expires_in
        self.access_token = access_token


class AzureClient:
    redirect_url = None
    client_id = None
    scope = None
    state = uuid.uuid4().hex  # used to prevent CSRF
    microsoft_login_url = "login.microsoftonline.com"
    conn = http.client.HTTPSConnection(microsoft_login_url)
    on_token_success = None
    token = None

    @classmethod
    def setup(
        self,
        redirect_url: str,
        client_id: str,
        scope: str,
        on_token_success: callable,
    ) -> None:
        AzureClient.redirect_url = redirect_url
        AzureClient.client_id = client_id
        AzureClient.scope = scope
        AzureClient.on_token_success = on_token_success

    @classmethod
    def authorise(self) -> None:
        url = "https://{}/common/oauth2/v2.0/authorize?client_id={}&response_type=code&response_mode=query&scope={}&state={}&redirect_uri={}".format(
            AzureClient.microsoft_login_url,
            AzureClient.client_id,
            url_encode.quote(AzureClient.scope),
            AzureClient.state,
            url_encode.quote(AzureClient.redirect_url),
        )
        success = webbrowser.open_new_tab(url)
        if not success:
            raise Exception("Authorisation failed")
        # response will be received via a GET to AzureServerHandler

    @classmethod
    def get_token(self, authorisation_code: str, csrf_state: str) -> None:
        if csrf_state != AzureClient.state:
            raise Exception("CSRF detected")

        payload = "client_id={}&scope={}&code={}&redirect_uri={}&grant_type=authorization_code".format(
            AzureClient.client_id,
            url_encode.quote(AzureClient.scope),
            authorisation_code,
            url_encode.quote(AzureClient.redirect_url),
        )

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }

        AzureClient.conn.request("POST", "/common/oauth2/v2.0/token", payload, headers)

        response = AzureClient.conn.getresponse()
        if response.status != 200:
            raise Exception("Authorisation failed")

        res_bytes = response.read()
        res_json = json.loads(res_bytes)

        AzureClient.on_token_success(
            res_json["token_type"],
            res_json["scope"],
            res_json["expires_in"],
            res_json["access_token"],
        )
