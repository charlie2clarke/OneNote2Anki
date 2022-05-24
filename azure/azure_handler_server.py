import json
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer


class AzureAuthoriseServer:
    def __init__(
        self,
        host_name: str,
        port: int,
        on_authorise_sucess: callable,
    ):
        AzureHandlerServer.on_authorise_sucess = on_authorise_sucess
        self.server = HTTPServer((host_name, port), AzureHandlerServer)

    def start(self) -> None:
        self.server.serve_forever()

    def close(self) -> None:
        self.server.server_close()


class AzureHandlerServer(BaseHTTPRequestHandler):
    on_authorise_sucess = None

    def _set_response(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def do_GET(self):
        # Azure AD sends a second get request for a favicon
        if self.path != "/favicon.ico":
            url_params = urllib.parse.parse_qs(self.path[2:])

            if "error_description" in url_params:
                raise Exception("Authorisation failed")

            authorisation_code = url_params["code"][0]
            csrf_state = url_params["state"][0]
            self._set_response()
            AzureHandlerServer.on_authorise_sucess(authorisation_code, csrf_state)

    def do_POST(self):
        content_length = int(self.headers["Content-Length"])
        post_data_str = self.rfile.read(content_length)
        post_data = json.loads(post_data_str)
        self._set_response()
