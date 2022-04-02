from __future__ import annotations

import xml.etree.ElementTree as ET
from typing import Literal, Tuple, Union

from httpx import BasicAuth, DigestAuth, Response


Auth = Union[
    Tuple[str, str], BasicAuth, DigestAuth
]  # (email, pw) | BasicAuth | DigestAuth
Cert = Union[str, Tuple[str, str]]  # path-to-cert.pem | ('cert', 'key')
RequestMethod = Literal["PROPFIND", "GET", "PUT", "DELETE", "MKCOL", "HEAD", "POST"]
# there are more methods, we'll see how many we can implement in time


class DAVException(Exception):
    """Raised when a WebDAV operation fails."""


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
            raise DAVException()  # TODO: better error displays

    def xml(self) -> ET.Element:
        """Parses the response XML content."""
        return ET.fromstring(self._orig.content)

    def __repr__(self) -> str:
        return f"<DAVResponse [{self._orig.status_code}]>"
