import asyncio

from pywebdav import AsyncWebDAVClient


async def download(client: AsyncWebDAVClient, path: str, fp: str) -> None:
    r = await client._request("GET", path)
    with open(fp, "wb") as f:
        f.write(r._orig.read())


async def main() -> None:
    host = "demo.owncloud.com"
    path = "remote.php/dav/files/demo"  # of format remote.php/dav/files/USERNAME
    auth = ("demo", "demo")
    client = AsyncWebDAVClient(host, auth=auth, path=path)
    r = await client._request("PROPFIND", "/", headers={"Depth": "1"})
    print(r)
    elem = r.xml()
    await client.close()


asyncio.run(main())
