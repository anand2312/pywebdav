from __future__ import annotations

import xml.etree.ElementTree as ET
from typing import Union

from .types import CollectionProperties, FileProperties, DAVResponse, Resource


__all__ = ["DEFAULT_HEADERS", "form_path", "response_to_resources"]


DEFAULT_HEADERS = {"Content-Type": "application/xml"}


def form_path(cwd: str, path: str) -> str:
    """Compute the final path from the given cwd and target path."""
    # inspired by
    # https://github.com/amnong/easywebdav/blob/440c6132bcdd04a5618e6b0a6d0151a1c6cec1ad/easywebdav/client.py#L109
    cwd_parts = [part for part in cwd.split("/") if part != ""]
    dest_parts = [part for part in path.strip().split("/") if part != ""]

    if len(dest_parts) == 0:
        return cwd

    if dest_parts[0] == ".":
        # ignore single dot if it is present
        dest_parts = dest_parts[1:]

    if dest_parts[0] == "..":
        while len(dest_parts) >= 1 and dest_parts[0] == "..":
            # remove the last part of the cwd, then add in the target path
            cwd_parts = cwd_parts[:-1]
            dest_parts = dest_parts[1:]
        else:
            result = "/".join(cwd_parts) + "/" + "/".join(dest_parts) + "/"
    else:
        if path.startswith("/"):
            result = "/" + "/".join(dest_parts) + "/"
        else:
            result = cwd + "/".join(dest_parts) + "/"

    if result.strip("/") == "":
        # the end result was just a sequence of backslashes
        # in which case, just return a single backslash i.e root dir
        return "/"
    else:
        return result


def response_to_resources(res: DAVResponse) -> list[Resource]:
    """
    Converts a DAVResponse into a list of Resource objects (if possible). Meant to be used with
    a PROPFIND request.
    """
    resources: list[Resource] = []
    for child in res.xml().findall("{DAV:}response"):
        href = _get_child_named(child, "href", "")
        href = href or ""  # will not happen, here for type checking
        props_elem = child.findall("{DAV:}propstat/{DAV:}prop")[0]
        if props_elem is None:
            props = {}
        else:
            props = _parse_properties(props_elem)

        status = _get_child_named(child, "status", "")
        resources.append(Resource(href=href, properties=props, status=status))  # type: ignore
    return resources


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
