from __future__ import annotations

from pathlib import Path
from typing import List, Literal, Optional, Tuple, Union

from . import SyncWebDAVClient
from .types import DAVResponse, Resource
from .utils import form_path, response_to_resources


class ShellDAVClient:
    """
    Handles a shell session.
    Note: This currently only allows synchronous operations.
    """

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

    def ls(
        self,
        path: str,
        *,
        depth: Literal["1", "0", "infinity"] = "1",
        properties: Optional[List[str]] = None,
    ) -> List[Resource]:
        """List files/folders."""
        path = form_path(self.cwd, path)
        res = self.dav_client.propfind(path, depth=depth, properties=properties)
        res.raise_for_status()
        resources = response_to_resources(res)
        if resources:
            resources = resources[1:]  # the first entry is the root
        return resources

    def mkdir(self, dirname: str) -> DAVResponse:
        """Create a new folder."""
        return self.dav_client.mkcol(form_path(self.cwd, dirname))

    def download(self, src_path: str, destination_fp: Union[str, Path]) -> None:
        """Downloads a file located at src_path and saved it into destination_fp."""
        path = form_path(self.cwd, src_path)
        res = self.dav_client.get(path)
        res.raise_for_status()

        with open(destination_fp, "wb") as f:
            f.write(res._orig.read())

    def upload(self, destination_path: str, source_fp: Union[str, Path]) -> None:
        """Uploads source_fp to destination_path."""
        path = form_path(self.cwd, destination_path)
        with open(source_fp, "rb") as f:
            res = self.dav_client.put(path, content=f.read())
        res.raise_for_status()

    def cd(self, dest: str) -> None:
        cwd = form_path(self.cwd, dest).strip("/")
        if cwd == "":
            self.cwd = "/"
        else:
            self.cwd = "/" + cwd + "/"
