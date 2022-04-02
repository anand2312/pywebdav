from httpx import AsyncClient as AsyncClient
from httpx import Client as _Client


# done to accomodate for unasync code generation
class SyncClient(_Client):
    def aclose(self) -> None:
        super().close()


DEFAULT_HEADERS = {"Content-Type": "application/xml"}
