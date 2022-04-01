from __future__ import annotations
from email import header
from types import TracebackType

from typing import Any, Literal, Optional

from ..utils import AsyncClient, DEFAULT_HEADERS
from ..types import Auth, Cert, DAVResponse, RequestMethod


class AsyncWebDAVClient:
    base_url: str
    _client: AsyncClient

    def __init__(
        self,
        host: str,
        port: int = 0,
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

        self._client = AsyncClient(**args)

    async def close(self) -> None:
        """Closes the underlying HTTP transports and proxies."""
        await self._client.aclose()

    async def __aenter__(self) -> AsyncWebDAVClient:
        return self

    async def __aexit__(
        self, exc_type: type[BaseException], exc_value: BaseException, tb: TracebackType
    ) -> None:
        await self.close()

    async def _request(
        self,
        method: RequestMethod,
        path: str,
        headers: Optional[dict[str, str]] = None,
        **kwargs: Any,
    ) -> DAVResponse:
        req_headers = {**DEFAULT_HEADERS}
        if headers is not None:
            req_headers.update(headers)
        res = await self._client.request(method, path, headers=req_headers, **kwargs)
        return DAVResponse(res)
