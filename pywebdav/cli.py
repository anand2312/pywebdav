import json
import shlex
from http.client import responses
from pathlib import Path
from typing import Any, Optional, Tuple

import httpx
from typer import Exit, Option, Typer, echo

from .shell_client import ShellDAVClient
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
        None,
        help="Headers to pass with the request. Make sure to properly escape quotes!",
        show_default=False,
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
    status = f"{res.status_code} {responses.get(res.status_code, 'UNKNOWN')}"
    echo(f"Status: {status}\n")
    echo(res.text)


@app.command()
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
    auth = _handle_username_pw(username, password)
    _shell_main(
        host=host,
        port=port,
        scheme="https" if use_https else "http",
        auth=auth,
        path=path,
    )
    raise Exit()


def _shell_main(**kwargs: Any) -> None:
    """REPL for shell commands"""
    client = ShellDAVClient(**kwargs)
    cmd_mapping = {"ls": ls_cmd, "cd": cd_cmd, "help": help_cmd}
    echo(f"pywebdav shell")
    echo(f"Connecting to {client.dav_client.base_url}")
    echo("Type 'help' for a list of commands, and 'exit' to leave the shell.")

    while True:
        line = input(f"{client.cwd}> ")
        cmd_name, *args = shlex.split(line)

        if cmd_name == "exit":
            client.dav_client.close()
            break

        cmd_func = cmd_mapping.get(cmd_name)

        if cmd_func is None:
            echo(f"Invalid command: {cmd_name}")
            continue

        cmd_func(client, *args)
        continue


def ls_cmd(client: ShellDAVClient, dest: Optional[str] = None) -> None:
    path = client.cwd if dest is None else dest
    resources = client.ls(path)
    out = "\n".join([res.basename for res in resources])
    echo(out)


def cd_cmd(client: ShellDAVClient, dest: str) -> None:
    client.cd(dest)


def help_cmd(_: ShellDAVClient, cmd: Optional[str] = None) -> None:
    cmd_help_mapping = {
        "cd": (
            "Change directory.\n\n"
            "Arguments:\n"
            "   destination: The destination path [REQUIRED]"
        ),
        "ls": (
            "List files and folders.\n\n"
            "Arguments:\n"
            "   path: Path to the directory whose files should be listed."
            " If not passed, lists files in current directory."
        ),
        "upload": (""),
        "download": (""),
        "exit": "Ends the shell session",
    }
    main_help = (
        "pywebdav shell\n"
        "Some commands to interact with the filesystem.\n\n"
        "Commands:\n" + " " * 4 + ", ".join(cmd_help_mapping.keys())
    )

    echo(cmd_help_mapping.get(cmd, main_help))  # type: ignore
