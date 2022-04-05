# unasync generates the sync client automatically from the async client
# some names need to be modified however for it to work
# without this, it would try importing a SyncClient class from httpx,
# which does not exist.
from httpx import AsyncClient as AsyncClient
from httpx import Client as BaseClient


class SyncClient(BaseClient):
    def aclose(self) -> None:
        return super().close()
