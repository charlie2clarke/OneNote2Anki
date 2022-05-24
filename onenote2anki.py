import logging
from threading import Thread

from azure.azure_client import AzureClient, Token
from azure.azure_handler_server import AzureAuthoriseServer
from setting.setting import azure_setting, server_setting, setting_setup


def on_authorise_success(authorisation_code: str, csrf_state: str) -> None:
    logging.info("authorisation (1st step) success")
    AzureClient.get_token(authorisation_code, csrf_state)


def on_token_success(
    token_type: str, scope: str, expires_in: int, access_token: str
) -> None:
    logging.info("token received")
    token = Token(token_type, scope, expires_in, access_token)
    AzureClient.token = token
    logging.info(AzureClient.token)


def run() -> None:
    logging.basicConfig(level=logging.INFO)
    setting_setup()

    # server setup
    server = AzureAuthoriseServer(
        server_setting.host_name,
        server_setting.port,
        on_authorise_success,
    )
    logging.info(
        "Server started http://%s:%s"
        % (server_setting.host_name, str(server_setting.port))
    )

    try:
        thread = Thread(target=server.start)
        thread.start()
    except KeyboardInterrupt:
        server.close()
        logging.info("Server stopped.")

    AzureClient.setup(
        "http://{}:{}".format(server_setting.host_name, server_setting.port),
        azure_setting.client_id,
        azure_setting.scope,
        on_token_success,
    )

    try:
        AzureClient.authorise()
    except Exception as e:
        logging.error(e)


run()
