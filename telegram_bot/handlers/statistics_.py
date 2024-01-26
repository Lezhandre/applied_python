from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.state import default_state

from .statistics_middleware import statistics

router = Router()


@router.message(Command("stats"), default_state)
async def cmd_stats(message: Message):
    await message.answer(str(statistics))
