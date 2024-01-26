from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message
from aiogram.types import ReplyKeyboardRemove


class Statistics(BaseMiddleware):
    """
    Мидлварь для сбора статистики
    """
    files = 0
    objects = 0
    model_trains = 0
    crashes = 0

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        try:
            result = await handler(event, data)
            if result is not None:
                setattr(self, result.value, getattr(self, result.value) + 1)
        except:
            if 'state' in data:
                await data['state'].clear()
            await event.answer('Что-то пошло совсем не так', reply_markup=ReplyKeyboardRemove())
            self.crashes += 1

    def __str__(self):
        return (
            f'Файлов отправлено\t:\t{self.files}\n'
            f'Объектов отправлено\t:\t{self.objects}\n'
            f'Моделей создано\t:\t{self.model_trains}\n'
            f'Крашей\t:\t{self.crashes}\n'
        )


statistics = Statistics()
