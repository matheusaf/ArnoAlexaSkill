# import requests as req
import aiohttp as req

"""
    Http Client cLass
"""


class HttpClient:
    __slots__ = [
        "__session_"
    ]

    __session_: req.ClientSession

    def __init__(self, session: req.ClientSession) -> None:
        self.__session_ = session

    async def get(self, url: str, headers={}) -> object:
        return await self.__session_.get(url, headers=headers)

    async def patch(
        self, url: str, 
        body: object, 
        headers={"Content-type": "application/json"}
    ) -> object:
        return await self.__session_.patch(url, data=body, headers=headers)
