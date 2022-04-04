import asyncio

from pywebdav import AsyncWebDAVClient


host = "demo.owncloud.com"
path = "remote.php/dav/files/demo"  # of format remote.php/dav/files/USERNAME
auth = ("demo", "demo")

client = AsyncWebDAVClient(host, auth=auth, path=path)


async def propfind() -> None:
    r = await client.request("PROPFIND", "/", headers={"Depth": "1"})
    print(r)
    elem = r.xml()
    # do stuff with the element


async def download(path: str, fp: str) -> None:
    r = await client.request("GET", path)
    with open(fp, "wb") as f:
        f.write(r._orig.read())


async def main() -> None:
    await propfind()
    await download("/Images/Portugal.jpg", "portugal.jpg")
    await client.close()


asyncio.run(main())
