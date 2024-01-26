from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.state import default_state

router = Router()


@router.message(Command("help"), default_state)
async def cmd_help(message: Message):
    await message.answer(
        '/get_columns - названия колонок, на которых обучаются модели\n'
        '/train - тренировка (новой) модели\n'
        '/model_info - информация о модели\n'
        '/predict - предсказание модели по объекту/данным\n'
        '/cancel - отменяет выбор действия\n'
        '/stats - вывод статистики\n'
        '/help - вывод этой справки\n'
    )
