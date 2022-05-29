from main import dp, bot
from aiogram.types import Message
from bot.keyboards.start_menu_keyboard import get_start_menu
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3 as sl
import os
from tinkoff.invest import Client
from config.personal_data import get_token

"""

    Тут представлены все хэндлеры, которые отвечают за добавление токена

"""

"""
    Первый хэндлер, который запускает состояние продажи
"""


@dp.message_handler(state="*", text="Открыть песочницу")
async def choose_account(message: Message):

    with Client(get_token(message.from_user.id)) as client:
        acc = client.sandbox.get_sandbox_accounts().accounts
        if len(acc) == 0:
            client.sandbox.open_sandbox_account()
        else:
            await message.answer("У Вас уже есть аккаунт в песочнице!",
                                 reply_markup=get_start_menu(user_id=message.from_user.id))


@dp.message_handler(state="*", text="Закрыть песочницу")
async def choose_account(message: Message):

    with Client(get_token(message.from_user.id)) as client:
        acc = client.sandbox.get_sandbox_accounts().accounts

        if len(acc) == 0:
            await message.answer("У Вас ещё нет аккаунта в песочнице!:",
                                 reply_markup=get_start_menu(user_id=message.from_user.id))
        else:
            delete_sandbox = InlineKeyboardMarkup()
            for i in acc:
                delete_sandbox.add(InlineKeyboardButton(text=f"{i.id}", callback_data=f"sandbox:close:{i.id}"))

            await message.answer("Выберите аккаунт:",
                                 reply_markup=delete_sandbox)


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('sandbox:close'))
async def close_order(callback_query):

    data = callback_query.data.split(":")

    account_id = data[2]

    with Client(get_token(callback_query.from_user.id)) as client:
        client.sandbox.close_sandbox_account(account_id=account_id)

