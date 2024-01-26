from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.types import Message
from aiogram.fsm.state import StatesGroup, State, default_state
from aiogram.fsm.context import FSMContext
from aiogram.types.input_file import BufferedInputFile

from .statistics_middleware import statistics
from .keyboards import train_model_kbs, data_format_kbs

import csv
import json
import requests
from io import BytesIO, StringIO
from enum import Enum

router = Router()
router.message.middleware(statistics)
model_url = 'http://localhost:8000/'


class ModelSelection(StatesGroup):
    choosing_linear_model = State()
    choosing_error_function = State()


class DataPreparation(StatesGroup):
    choosing_format = State()
    downloading_file = State()
    downloading_object = State()
    cancel_operations = State()


class Event(Enum):
    File = 'files'
    Object = 'objects'
    Train = 'model_trains'
    Crash = 'crashes'


async def next_keyboard(state: FSMContext):
    kb_iter = (await state.get_data())['keyboard']
    ret = await anext(kb_iter)
    await state.update_data(keyboard=kb_iter)
    return ret


@router.message(Command("train"), default_state)
async def cmd_train(message: Message, state: FSMContext):
    await state.set_data({'keyboard': aiter(train_model_kbs())})
    await state.set_state(ModelSelection.choosing_linear_model)
    await message.answer(
        'Выберите линейную модель регрессии (можно не только из преложенных, но из sklearn.linear_model).',
        reply_markup=await next_keyboard(state)
    )


@router.message(StateFilter(ModelSelection.choosing_linear_model))
async def cmd_train(message: Message, state: FSMContext):
    await state.update_data({'model_name': message.text})
    await state.set_state(ModelSelection.choosing_error_function)
    await message.answer('Выберите функцию ошибки.', reply_markup=await next_keyboard(state))


@router.message(StateFilter(ModelSelection.choosing_error_function))
async def cmd_train(message: Message, state: FSMContext):
    await state.update_data({'func_score': message.text})
    response = requests.patch(model_url + 'train_model/', params=await state.get_data())
    if not response.ok:
        await message.answer('Что-то пошло не так.', reply_markup=await next_keyboard(state))
        await state.clear()
        return Event.Crash
    else:
        await message.answer(
            f'Модель обучилась предсказывать откликнется ли клиент на предложения '
            f'с оценкой {response.content.decode()}.',
            reply_markup=await next_keyboard(state)
        )
        await state.clear()
    return Event.Train


@router.message(Command("get_columns"), default_state)
async def cmd_get_columns(message: Message):
    response = requests.get(model_url + 'column_names', message.text)
    array = json.loads(response.content)
    await message.answer('Колонки данных:\n' + '\n'.join(array) + '.')


@router.message(Command("predict"), default_state)
async def cmd_predict(message: Message, state: FSMContext):
    await state.set_data({'keyboard': aiter(data_format_kbs())})
    await state.set_state(DataPreparation.choosing_format)
    await message.answer(
        'Выберите вариант отправки данных для получения по ним ответа моделью.',
        reply_markup=await next_keyboard(state)
    )


@router.message(StateFilter(DataPreparation.choosing_format))
async def cmd_predict(message: Message, state: FSMContext):
    match message.text:
        case 'File':
            await state.set_state(DataPreparation.downloading_file)
            answer_text = ('Отправьте csv-файл и модель даст ответ '
                           '(придёт в виде файла с дополнительной колонкой \'TARGET\').')
        case 'Object':
            await state.set_state(DataPreparation.downloading_object)
            answer_text = ('Можете вводить объекты или отправлять файлы с объектом в json-формате. '
                           'Как только надоест, можно отменить ввод при помощи команды /cancel.')
        case _:
            await message.answer(
                'Выбрать можно только один из 2-ух предложенных вариантов (увы).',
                reply_markup=await next_keyboard(state)
            )
            await state.clear()
            return
    await message.answer(
        answer_text,
        reply_markup=await next_keyboard(state)
    )


@router.message(StateFilter(DataPreparation.downloading_file))
async def cmd_predict(message: Message, state: FSMContext):
    with BytesIO() as file_input:
        await message.bot.download(message.document, file_input)
        csv_input = file_input.read().decode()

    response = requests.patch(model_url + 'predict/', csv_input)
    await message.answer_document(
        BufferedInputFile(response.content, 'model_answer.csv'),
        reply_markup=await next_keyboard(state)
    )
    await state.clear()
    return Event.File


@router.message(StateFilter(DataPreparation.downloading_object))
async def cmd_predict(message: Message, state: FSMContext):
    if message.document is not None:
        with BytesIO() as file_input:
            await message.bot.download(message.document, file_input)
            json_input = json.load(file_input)
        ret = Event.File
    else:
        json_input = json.loads(message.text)
        ret = Event.Object

    with StringIO() as csv_buffer:
        writer = csv.DictWriter(csv_buffer, fieldnames=json_input.keys())

        writer.writeheader()
        writer.writerow(json_input)
        csv_buffer.flush()

        csv_input = csv_buffer.getvalue()

    response = requests.patch(model_url + 'predict/', csv_input)
    with StringIO(response.content.decode(), newline='') as csv_response:
        reader = csv.DictReader(csv_response)
        for row in reader:
            await message.answer(
                f'Вероятность, что клиент откликнется на предложение банка, согласно модели: {row["TARGET"]}.',
                reply_markup=await next_keyboard(state)
            )
    return ret


@router.message(Command("model_info"), default_state)
async def cmd_model_info(message: Message):
    response = requests.get(model_url + 'model_info')
    await message.answer(
        'Информация о модели:\n' +
        '\n'.join(str(n) + ' = ' + str(v) for n, v in json.loads(response.content).items()) +
        '.'
    )
