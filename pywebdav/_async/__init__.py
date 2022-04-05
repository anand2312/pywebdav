from __future__ import annotations

import xml.etree.ElementTree as ET
from types import TracebackType

from typing import Any, List, Literal, Optional

from .._unasync_compat import AsyncClient
from ..types import Auth, Cert, DAVResponse, RequestMethodLiteral
from ..utils import DEFAULT_HEADERS


class AsyncWebDAVClient:
    base_url: str
    _client: AsyncClient

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

    async def request(
        self,
        method: RequestMethodLiteral,
        path: str,
        **kwargs: Any,
    ) -> DAVResponse:
        """Run an arbitrary DAV request.

        Args:
            method: The request method to be used
            path: The path to send the request to

        Note:
            1) Any extra kwargs passed to this method are directly passed
            unchanged to [`httpx.request`](https://www.python-httpx.org/api/#helper-functions)
            2) If a headers kwarg is passed, it will be merged with the default headers before
            sending the request.
        """
        req_headers = {**DEFAULT_HEADERS}
        extra_headers = kwargs.get("headers")
        if extra_headers is not None:
            req_headers.update(extra_headers)

        res = await self._client.request(method, path, headers=req_headers, **kwargs)
        return DAVResponse(res)

    async def propfind(
        self,
        path: str,
        *,
        depth: Literal["0", "1", "infinity"] = "1",
        properties: Optional[List[str]] = None,
    ) -> DAVResponse:
        """Runs a PROPFIND request.

        Args:
            path: The path to send the request to
            depth: Depth of the listing
            properties: List of properties to request.
        """
        if not path.endswith("/"):
            path += "/"

        if properties:
            root = ET.Element(
                "d:propfind",
                {
                    "xmlns:d": "DAV:",
                    "xmlns:oc": "http://owncloud.org/ns",
                },
            )
            prop = ET.SubElement(root, "d:prop")
            for i in properties:
                ET.SubElement(prop, i)
            content = ET.tostring(root)
        else:
            content = None

        return await self.request(
            "PROPFIND", path, headers={"Depth": depth}, content=content
        )

    async def mkcol(self, path: str) -> DAVResponse:
        """Runs an MKCOL request.

        Args:
            path: The path to send the request to
        """
        if not path.endswith("/"):
            path += "/"
        return await self.request("MKCOL", path)

    async def get(self, path: str, **kwargs: Any) -> DAVResponse:
        """Runs a GET request.

        Args:
            path: The path to send the request to

        Note:
            Any extra kwargs passed to this method are directly passed
            unchanged to [`httpx.request`](https://www.python-httpx.org/api/#helper-functions)
        """
        return await self.request("GET", path, **kwargs)

    async def put(self, path: str, *, content: bytes, **kwargs: Any) -> DAVResponse:
        """Runs a PUT request.

        Args:
            path: The path to send the request to
            content: The content to be sent

        Note:
            Any extra kwargs passed to this method are directly passed
            unchanged to [`httpx.request`](https://www.python-httpx.org/api/#helper-functions)
        """
        return await self.request("PUT", path, content=content, **kwargs)
