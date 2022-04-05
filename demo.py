import asyncio

from pywebdav import AsyncWebDAVClient

# from pywebdav import SyncWebDAVClient -- synchronous client!
from pywebdav.utils import response_to_resources


host = "demo.owncloud.com"
path = "remote.php/dav/files/demo"
auth = ("demo", "demo")

client = AsyncWebDAVClient(host, auth=auth, path=path)


async def main() -> None:
    # propfind - list directories/files
    res = await client.propfind("/", depth="1")
    files = response_to_resources(res)
    print(files)
    # files is now a list of Resource objects, that have been parsed from the XML response

    # get - retrieve a file
    res = await client.get("/Images/Portugal.jpg")
    with open("portugal.jpg", "wb") as f:
        f.write(res.read())

    # put - upload a file
    with open("portugal.jpg", "rb") as f:
        await client.put("/Documents/portugal.jpg", content=f.read())

    await client.close()
    # all the methods have synchronous counterparts that work exactly the same;
    # just import the synchronous client instead.


asyncio.run(main())
