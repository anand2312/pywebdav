import xml.etree.ElementTree as ET
from io import BufferedIOBase

import pytest
import pytest_asyncio

from pywebdav import AsyncWebDAVClient


@pytest_asyncio.fixture()
async def client():
    async with AsyncWebDAVClient(
        host="demo.owncloud.com",
        auth=("demo", "demo"),
        path="remote.php/dav/files/demo",
    ) as client:
        yield client


@pytest_asyncio.fixture(scope="function", autouse=True)
async def is_oc_server_up(client: AsyncWebDAVClient):
    # the owncloud server is automatically reset every hour
    # when it is getting reset, it returns a 404 NOT FOUND to every request
    # skip runnning tests if this is the case.
    res = await client.propfind(
        "/"
    )  # propfinding the root directory should return 20x response
    if res.status_code == 404:
        pytest.skip(
            "The owncloud demo server is currently being reset. Run the tests again in a few minutes.",
            allow_module_level=True,
        )


@pytest.fixture
def test_file():
    with open("README.md", "rb") as f:
        yield f


@pytest_asyncio.fixture()
async def test_file_upload(client: AsyncWebDAVClient, test_file: BufferedIOBase):
    yield test_file
    # this fixture is used in the test_put_201 test
    # after uploading the file, we need to clean up
    # after ourselves
    await client.delete("/testing--readme.md")


@pytest.mark.asyncio
async def test_propfind_207(client: AsyncWebDAVClient):
    res = await client.propfind("/")
    assert res.status_code == 207
    assert res.xml()  # make sure that some XML response was returned


@pytest.mark.asyncio
async def test_propfind_404(client: AsyncWebDAVClient):
    res = await client.propfind("/non-existent-path")
    assert res.status_code == 404
    with pytest.raises(ET.ParseError):
        res.xml()  # no xml data would be returned


@pytest.mark.asyncio
async def test_put_409(client: AsyncWebDAVClient, test_file: BufferedIOBase):
    res = await client.put("/non-existent-path/README.md", content=test_file.read())
    assert (
        res.status_code == 409
    )  # cannot create file.md as parent non-existent-path would not exist.
    print(res.xml())


@pytest.mark.asyncio
async def test_put_201(client: AsyncWebDAVClient, test_file_upload: BufferedIOBase):
    res = await client.put("/testing--readme.md", content=test_file_upload.read())
    assert res.status_code == 201


@pytest.mark.asyncio
async def test_get_200(client: AsyncWebDAVClient):
    res = await client.get("/Photos/Portugal.jpg")
    assert res.status_code == 200


@pytest.mark.asyncio
async def test_get_404(client: AsyncWebDAVClient):
    res = await client.get("/non-existent-path")
    assert res.status_code == 404
