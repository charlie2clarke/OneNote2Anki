import json
from types import SimpleNamespace


class Server:
    host_name: str
    port: int


class Azure:
    microsoft_login_url: str
    client_id: str
    scope: str


server_setting = Server()
azure_setting = Azure()


def setting_setup() -> None:
    conf_file = open("conf/conf.json", "r")
    conf = json.load(conf_file, object_hook=lambda d: SimpleNamespace(**d))

    server_setting.host_name = conf.server.host_name
    server_setting.port = conf.server.port

    azure_setting.microsoft_login_url = conf.azure.microsoft_login_url
    azure_setting.client_id = conf.azure.client_id
    azure_setting.scope = conf.azure.scope
