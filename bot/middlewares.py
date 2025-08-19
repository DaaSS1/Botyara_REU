from aiogram import BaseMiddleware
from aiogram.types import Message
from typing import Callable, Dict, Any, Awaitable, List
import asyncio

class AlbumMiddleware(BaseMiddleware):
    """
    Склеивает сообщения с одинаковым media_group_id (альбом).
    """

    def __init__(self, latency: float = 0.2):
        # задержка нужна, чтобы успели прийти все фото в альбоме
        self.latency = latency
        self.albums: Dict[str, List[Message]] = {}

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        if not event.media_group_id:
            return await handler(event, data)

        # если это часть альбома — копим
        group_id = event.media_group_id
        album = self.albums.setdefault(group_id, [])
        album.append(event)

        # ждём, чтобы Telegram успел прислать все фото из альбома
        await asyncio.sleep(self.latency)

        # если это последнее фото — вызываем хендлер один раз
        if album and album[0] == event:
            data["album"] = album.copy()
            del self.albums[group_id]
            return await handler(event, data)
