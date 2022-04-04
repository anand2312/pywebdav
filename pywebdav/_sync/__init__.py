from __future__ import annotations

from types import TracebackType


from typing import Any, Literal, Optional, Union


from ..utils import SyncClient, DEFAULT_HEADERS

from ..types import Auth, Cert, DAVResponse, RequestMethod, RequestMethodLiteral


class SyncWebDAVClient:

    base_url: str

    _client: SyncClient

    def __init__(
        self,
        host: str,
        port: int = 0,
        *,
        scheme: Literal["http", "https"] = "https",
        auth: Optional[Auth] = None,
        cert: Optional[Cert] = None,
        path: Optional[str] = None,
    ) -> None:

        """

        Initializes the WebDAV Client.



        Args:

            host: The server host

            port: The server port

            scheme: HTTP/HTTPS

            auth: Basic auth with a tuple of (username, password), or an instance of

                  [httpx.DigestAuth](https://www.python-httpx.org/quickstart/#authentication) for digest authentication.

            cert: Path to a certicate file, or a tuple of (cert, key)

            path: Any additional path which should be considered as part of the base URL.

        """

        if not port:

            port = 80 if scheme == "http" else 443

        self.base_url = f"{scheme}://{host}:{port}"

        if path:

            self.base_url += f"/{path}"

        args = {"auth": auth, "base_url": self.base_url}

        if cert is not None:

            args["cert"] = cert

        self._client = SyncClient(**args)

    def close(self) -> None:

        """Closes the underlying HTTP transports and proxies."""

        self._client.aclose()

    def __enter__(self) -> SyncWebDAVClient:

        return self

    def __exit__(
        self, exc_type: type[BaseException], exc_value: BaseException, tb: TracebackType
    ) -> None:

        self.close()

    def request(
        self,
        method: Union[RequestMethod, RequestMethodLiteral],
        path: str,
        headers: Optional[dict[str, str]] = None,
        **kwargs: Any,
    ) -> DAVResponse:

        req_headers = {**DEFAULT_HEADERS}

        if headers is not None:

            req_headers.update(headers)

        if isinstance(method, RequestMethod):

            # allows passing values of the RequestMethod enum

            # this enum is used in the CLI as typer has support for enums

            req_method = method.value

        else:

            req_method = method

        res = self._client.request(req_method, path, headers=req_headers, **kwargs)

        return DAVResponse(res)

    def propfind(
        self, path: str, *, body: str, depth: Literal["0", "1", "infinity"] = "1"
    ) -> DAVResponse:

        return self.request("PROPFIND", path, headers={"Depth": depth}, content=body)

    def get(self, path: str, **kwargs: Any) -> DAVResponse:

        return self.request("GET", path, **kwargs)

    def put(self, path: str, **kwargs: Any) -> DAVResponse:

        return self.request("PUT", path, **kwargs)
