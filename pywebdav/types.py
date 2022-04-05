from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Literal, Tuple, TypedDict, Union

from httpx import BasicAuth, DigestAuth, Response


Auth = Union[
    Tuple[str, str], BasicAuth, DigestAuth
]  # (email, pw) | BasicAuth | DigestAuth
Cert = Union[str, Tuple[str, str]]  # path-to-cert.pem | ('cert', 'key')
RequestMethodLiteral = Literal[
    "PROPFIND", "GET", "PUT", "DELETE", "MKCOL", "HEAD", "POST", "MOVE", "COPY"
]
# there are more methods, we'll see how many we can implement in time


class RequestMethod(str, Enum):
    PROPFIND = "PROPFIND"
    GET = "GET"
    PUT = "PUT"
    DELETE = "DELETE"
    MKDCOL = "MKCOL"
    HEAD = "HEAD"
    POST = "POST"
    MOVE = "MOVE"
    COPY = "COPY"


class DAVException(Exception):
    """Raised when a WebDAV operation fails."""

    def __init__(self, status: int, message: str = "") -> None:
        self.status_code = status
        super().__init__(
            f"Status: {status}\n{'Message: ' + message if message else ''}"
        )


class DAVResponse:
    def __init__(self, response: Response) -> None:
        self._orig = response

    @property
    def status_code(self) -> int:
        return self._orig.status_code

    def raise_for_status(self) -> None:
        try:
            self._orig.raise_for_status()
        except Exception as e:
            raise DAVException(self.status_code)  # TODO: better error displays

    def xml(self) -> ET.Element:
        """Parses the response XML content."""
        return ET.fromstring(self._orig.content)

    def __repr__(self) -> str:
        return f"<DAVResponse [{self._orig.status_code}]>"


class CollectionProperties(TypedDict):
    type: Literal["collection"]
    last_modified: str
    etag: str


class FileProperties(TypedDict):
    type: Literal["file"]
    last_modified: str
    etag: str
    size: int
    content_type: str


@dataclass
class Resource:
    """Represents a DAV resource"""

    href: str
    properties: Union[CollectionProperties, FileProperties]
    status: str

    @property
    def basename(self) -> str:
        """Returns the name of the file, excluding the rest of it's path."""
        return Path(self.href).name
