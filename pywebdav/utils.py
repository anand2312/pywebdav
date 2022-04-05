from __future__ import annotations
from ctypes import cast

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryFile
import xml.etree.ElementTree as ET
from typing import Literal, Optional, TypedDict, Union

from httpx import AsyncClient as AsyncClient
from httpx import Client as _Client

from pywebdav.types import DAVResponse


# done to accomodate for unasync code generation
class SyncClient(_Client):
    def aclose(self) -> None:
        super().close()


DEFAULT_HEADERS = {"Content-Type": "application/xml"}


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


def _get_child_named(elem: ET.Element, name: str, default: str) -> str:
    child = elem.find(f".//{{DAV:}}{name}")
    # return child.text if it is not None, else return an empty string
    # however if child is None, return the specified default
    return (child.text or "") if child is not None else default


def _parse_properties(elem: ET.Element) -> Union[CollectionProperties, FileProperties]:
    """Parse the properties element of a file or collection response."""
    props = {}
    resource_type_elem = elem.find(".//{DAV:}resourcetype")
    assert resource_type_elem is not None
    # the owncloud server returns a child <d:collection /> with the resourcetype element
    # in the case of collection responses
    # the resourcetype element has no children in the case of file responses.
    # TODO: investigate if this is standard
    if len(resource_type_elem) == 1:
        props["type"] = "collection"
    else:
        props["type"] = "file"

    props["last_modified"] = _get_child_named(elem, "getlastmodified", "")
    props["etag"] = _get_child_named(elem, "getetag", "")

    if props["type"] == "file":
        props["size"] = int(_get_child_named(elem, "getcontentlength", "0"))
        props["content_type"] = _get_child_named(elem, "getcontenttype", "")
    # TODO: implement this with type safety
    return props  # type: ignore


def response_to_files(res: DAVResponse) -> list[Resource]:
    """
    Converts a DAVResponse into a list of Resource objects (if possible). Meant to be used with
    a PROPFIND request.
    """
    resources: list[Resource] = []
    for child in res.xml().findall("{DAV:}response"):
        href = _get_child_named(child, "href", "")
        if href is None:  # will not happen; is here to appease type-checker
            href = ""
        props_elem = child.findall("{DAV:}propstat/{DAV:}prop")[0]
        if props_elem is None:
            props = {}
        else:
            props = _parse_properties(props_elem)

        status = _get_child_named(child, "status", "")
        resources.append(Resource(href=href, properties=props, status=status))  # type: ignore
    return resources
