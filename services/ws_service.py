from repositories import ws_repository
from repositories.ws_repository import WebSocketRepository, get_ws_repository
from fastapi import Depends


class WebSocketService:
    def __init__(self, ws_repository: WebSocketRepository):
        self.ws_repository = ws_repository

    async def get_path(self):
        return await self.ws_repository.get_path()


def get_ws_service(ws_repository: WebSocketRepository = Depends(get_ws_repository)) -> WebSocketService:
    return WebSocketService(ws_repository)
