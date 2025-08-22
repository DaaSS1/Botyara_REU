from aiogram import BaseMiddleware
from aiogram.types import Message
from typing import Callable, Dict, Any, Awaitable, List
import asyncio

class AlbumMiddleware(BaseMiddleware):
    """
    Склеивает сообщения с одинаковым media_group_id (альбом).
    """

    def __init__(self, latency: float = 3):
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

# class AlbumMiddlewarePerformer(BaseMiddleware):
#     """
#     Middleware для сбора фото/видео, отправленных альбомом (media_group).
#     Склеивает все сообщения с одним media_group_id в один список.
#     """
#
#     def __init__(self, delay: float = 0.4):
#         super().__init__()
#         self.delay = delay
#         self.albums: Dict[str, List[Message]] = {}
#
#     async def __call__(self, handler, event: Message, data: dict):
#         if not event.media_group_id:
#             return await handler(event, data)
#
#         group_id = event.media_group_id
#         album = self.albums.setdefault(group_id, [])
#         album.append(event)
#
#         await asyncio.sleep(self.delay)  # ждём пока весь альбом прилетит
#
#         # если это последний вызов — передаём альбом
#         if group_id in self.albums and event == self.albums[group_id][-1]:
#             data["album"] = self.albums.pop(group_id)
#             return await handler(event, data)