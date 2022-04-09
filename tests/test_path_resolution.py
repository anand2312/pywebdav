from typing import Tuple
from pywebdav.utils import form_path

import pytest


parameters = [
    (("/", "/"), "/"),
    (
        ("/", "/a/b"),
        "/a/b/",
    ),  # the target is an absolute path; the end path should just be the target
    (("/a/b/", "c/d"), "/a/b/c/d/"),  # target is relative to cwd
    (("/a/", ".."), "/"),  # move one directory back
    (("/", ".."), "/"),  # attempting to move back from cwd does nothing
    (("/", "./test"), "/test/"),  # navigate to a directory contained in the cwd
]


@pytest.mark.parametrize("case,expected", parameters)
def test_path_resolution(case: Tuple[str, str], expected: str):
    """Test the function used by the shell to resolve relative paths."""
    cwd, target = case
    path = form_path(cwd, target)
    assert path == expected
