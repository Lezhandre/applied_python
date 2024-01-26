import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.filters import StateFilter, Command

from config_reader import config
from handlers import all_routers
from aiogram.fsm.strategy import FSMStrategy


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    dp = Dispatcher(fsm_strategy=FSMStrategy.CHAT)
    bot = Bot(config.bot_token.get_secret_value())

    dp.include_routers(*all_routers)

    @dp.message(Command("start"), StateFilter(None))
    async def cmd_help(message: Message):
        await message.answer(
            'Добро пожаловать в бот для моделей обученных на данных об откликах клиентов на предложения банка\n'
            'Для получения дополнительной информации отправьте /help\n'
        )

    @dp.message(Command("cancel"))
    async def cmd_predict(_, state: FSMContext):
        await state.clear()

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
