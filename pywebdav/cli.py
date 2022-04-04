import json
from pathlib import Path
from typing import Dict, Literal, Optional, Tuple

import httpx
from typer import Exit, Option, Typer, echo

from . import SyncWebDAVClient
from .types import RequestMethod
from .utils import DEFAULT_HEADERS


app = Typer(
    name="pywebdav",
    help="Python WebDAV client",
    no_args_is_help=True,
    add_completion=False,
)


def _handle_username_pw(
    username: Optional[str], password: Optional[str]
) -> Optional[Tuple[str, str]]:
    if username is None and password is None:
        return None
    elif isinstance(username, str) and isinstance(password, str):
        return (username, password)
    else:
        echo("Both username and password must be passed", err=True)
        raise Exit()


@app.command(no_args_is_help=True)
def request(
    method: RequestMethod,
    url: str,
    headers: Optional[str] = Option(
        None, help="Headers to pass with the request", show_default=False
    ),
    username: Optional[str] = Option(
        None, "-u", help="The username to use while authenticating", show_default=False
    ),
    password: Optional[str] = Option(
        None, "-pw", help="The password to use while authenticating", show_default=False
    ),
    body: Optional[str] = Option(
        None,
        help="The request body. If both this and the body_path params are passed, this takes precedence",
        show_default=False,
    ),
    body_path: Optional[Path] = Option(
        None,
        help="Path to a file containing the body to be sent with the request",
        show_default=False,
    ),
) -> None:
    """Make a WebDAV request to the specified URL."""
    auth = _handle_username_pw(username, password)

    if body_path is None and body is None:
        req_body = None
    elif body is not None:
        req_body = body
    elif body_path is not None:
        req_body = body_path.read_text()
    else:
        req_body = None

    if headers is None:
        req_headers = DEFAULT_HEADERS
    else:
        parsed_headers = json.loads(headers)
        req_headers = {**DEFAULT_HEADERS, **parsed_headers}

    res = httpx.request(method.value, url, headers=req_headers, data=req_body, auth=auth)  # type: ignore
    # XML can be directly passed as data if passed with the right Content-Type header
    # however httpx has type-hinted body to be of type dict

    echo(f"Status: {res.status_code}\n")
    echo(res.text)


@app.command(no_args_is_help=True)
def shell(
    host: str = Option(..., "-h", help="The host address; example: demo.owncloud.com"),
    port: int = Option(0, help="The port to connect to"),
    use_https: bool = True,
    username: Optional[str] = Option(
        None, "-u", help="The username to use while authenticating"
    ),
    password: Optional[str] = Option(
        str, "-pw", help="The password to use while authenticating"
    ),
    path: Optional[str] = Option(
        str,
        help="Any additional path which should be considered as part of the base URL",
    ),
) -> None:
    """Start a shell session. Run commands like `cd`, `ls` etc on the specified host server, using WebDAV requests."""
    ...


class ShellDAVClient:
    """Handles a shell session."""

    def __init__(
        self,
        host: str,
        port: int,
        *,
        scheme: Literal["http", "https"],
        auth: Optional[Tuple[str, str]],
        path: Optional[str],
    ) -> None:
        self.dav_client = SyncWebDAVClient(
            host, port, scheme=scheme, auth=auth, path=path
        )
        self.cwd = "/"
