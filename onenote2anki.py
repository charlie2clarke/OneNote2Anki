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
    logging.info("token received: {}".format(access_token))
    token = Token(token_type, scope, expires_in, access_token)
    AzureClient.token = token
    initialise()


def initialise() -> None:
    logging.info("initialise")
    notebooks = AzureClient.get_notebooks()
    sections = AzureClient.get_sections(notebooks[0].id)
    pages = AzureClient.get_pages(sections[0].id)
    logging.info("we made it")


def run() -> None:
    logging.basicConfig(level=logging.INFO)
    setting_setup()

    # see https://docs.microsoft.com/en-us/graph/auth-v2-user for authorisation workflow.
    # on_authorise_success will be called following a redirected GET request to the AzureAuthoriseServer
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

    # on_token_success will be called-back during the last stage of authentication.
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
