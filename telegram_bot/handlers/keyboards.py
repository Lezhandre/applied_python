from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def get_func_score_keyboard() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="precision_score")
    kb.button(text="recall_score")
    kb.button(text="f1_score")
    # kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)


def get_model_name_keyboard() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="LogisticRegression")
    kb.button(text="Lasso")
    kb.button(text="SGDRegressor")
    kb.button(text="ElasticNet")
    return kb.as_markup(resize_keyboard=True)


async def train_model_kbs():
    yield get_model_name_keyboard()
    yield get_func_score_keyboard()
    yield ReplyKeyboardRemove()


def get_data_format_keyboard() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="File")
    kb.button(text="Object")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)


async def data_format_kbs():
    yield get_data_format_keyboard()
    yield ReplyKeyboardRemove()
    while True:
        yield None
