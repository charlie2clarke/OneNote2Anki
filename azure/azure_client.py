import datetime
import http.client
import json
import uuid
import webbrowser
from functools import wraps
from urllib import parse as url_encode
from models.notebook import Notebook
from models.section import Section
from models.page import Page
from typing import List


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


# Used to decorate methods that require authentication.
def requires_auth(f):
    """Wrapper function to prompt user to authenticate."""

    @wraps(f)
    def decorated(*args, **kwargs):
        if AzureClient.token.access_token is None:
            return AzureClient.authorise()
        if AzureClient.token.expires_in < datetime.datetime.now():
            # If the access token is expired, require the user to login again
            return AzureClient.authorise()
        return f(*args, **kwargs)

    return decorated


class AzureClient:
    redirect_url = None
    client_id = None
    scope = None
    state = uuid.uuid4().hex  # used to prevent CSRF
    microsoft_login_url = "login.microsoftonline.com"
    auth_conn = http.client.HTTPSConnection(microsoft_login_url)
    ms_graph = http.client.HTTPSConnection("graph.microsoft.com")
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

        AzureClient.auth_conn.request(
            "POST", "/common/oauth2/v2.0/token", payload, headers
        )

        response = AzureClient.auth_conn.getresponse()
        if response.status != 200:
            raise Exception("Authorisation failed")

        res_bytes = response.read()
        res_json = json.loads(res_bytes)

        if "error" in res_json:
            if "error_subcode" in res_json:
                error_description = res_json["error_subcode"]
            else:
                error_description = res_json["error_description"]
            error_msg = "Error: {} \n Reason: {}".format(
                res_json["error"], error_description
            )
            raise Exception(error_msg)

        expires_in = datetime.datetime.now() + datetime.timedelta(
            seconds=res_json["expires_in"]
        )

        AzureClient.on_token_success(
            res_json["token_type"],
            res_json["scope"],
            expires_in,
            res_json["access_token"],
        )

    @classmethod
    def _get(self, url: str) -> any:
        headers = {
            "Authorization": "Bearer {}".format(AzureClient.token.access_token),
        }
        AzureClient.ms_graph.request("GET", url, None, headers)
        response = AzureClient.ms_graph.getresponse()
        if response.status != 200:
            raise Exception("Error getting {}".format(url))
        res_bytes = response.read()
        return json.loads(res_bytes)

    @classmethod
    @requires_auth
    def get_notebooks(self) -> List[Notebook]:
        try:
            notebooks_json = self._get("/v1.0/me/onenote/notebooks")
        except Exception as e:
            raise Exception("Error getting notebooks: {}".format(e))

        notebooks = []
        for notebook_json in notebooks_json["value"]:
            notebooks.append(
                Notebook(
                    id=notebook_json["id"],
                    name=notebook_json["displayName"],
                    is_default=notebook_json["isDefault"],
                    last_modified_date_time=datetime.datetime.strptime(
                        notebook_json["lastModifiedDateTime"],
                        "%Y-%m-%dT%H:%M:%S.%fZ",
                    ),
                    sections_url=notebook_json["sectionsUrl"],
                )
            )

        return notebooks

    @classmethod
    @requires_auth
    def get_sections(self, notebook_id: str) -> List[Section]:
        try:
            sections_json = self._get(
                "/v1.0/me/onenote/notebooks/{}/sections".format(notebook_id)
            )
        except Exception as e:
            raise Exception("Error getting sections: {}".format(e))

        sections = []
        for section_json in sections_json["value"]:
            sections.append(
                Section(
                    id=section_json["id"],
                    name=section_json["displayName"],
                    is_default=section_json["isDefault"],
                    last_modified_date_time=datetime.datetime.strptime(
                        section_json["lastModifiedDateTime"],
                        "%Y-%m-%dT%H:%M:%S.%fZ",
                    ),
                    pages_url=section_json["pagesUrl"],
                )
            )

        return sections

    @classmethod
    @requires_auth
    def get_pages(self, section_id: str) -> List[Page]:
        try:
            pages_json = self._get(
                "/v1.0/me/onenote/sections/{}/pages".format(section_id)
            )
        except Exception as e:
            raise Exception("Error getting pages: {}".format(e))

        pages = []
        for page_json in pages_json["value"]:
            pages.append(
                Page(
                    id=page_json["id"],
                    name=page_json["displayName"],
                    is_default=page_json["isDefault"],
                    last_modified_date_time=datetime.datetime.strptime(
                        page_json["lastModifiedDateTime"], "%Y-%m-%dT%H:%M:%S.%fZ"
                    ),
                    content_url=page_json["contentUrl"],
                )
            )

        return pages
