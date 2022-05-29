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

"""

    Тут представлены все хэндлеры, которые отвечают за добавление токена

"""



"""
    Первый хэндлер, который запускает состояние продажи
"""

@dp.message_handler(state="*", text="Изменить Аккаунт")
async def choose_account(message: Message):

    conn = sl.connect("db/users.db")
    cur = conn.cursor()

    token = cur.execute('SELECT token FROM USER WHERE id = ? ', (message.from_user.id,)).fetchone()[0]

    choose_account = InlineKeyboardMarkup()

    with Client(str(token)) as client:
        acc = client.users.get_accounts()
        acc_sand = client.sandbox.get_sandbox_accounts()
        for i in acc.accounts:
            choose_account.add(InlineKeyboardButton(text=f"{i.name}", callback_data=f"account:{i.id}:{i.name}"))
        for i in acc_sand.accounts:
            choose_account.add(InlineKeyboardButton(text=f"Песочница", callback_data=f"account:{i.id}:sandbox"))

    await message.answer("Выберите аккаунт:", reply_markup=choose_account)

"""
    Второй хендлер, который испольняется в состоянии s_wait_figi
"""

@dp.callback_query_handler(lambda c: c.data and c.data.startswith("account"))
async def account_finish(callback_query):

    data = callback_query.data.split(":")

    account_id = data[1]
    account_type = data[2]

    conn = sl.connect("db/users.db")
    cur = conn.cursor()

    cur.execute('UPDATE USER SET account_id = ?, account_type = ? WHERE id = ?;', (account_id, account_type, callback_query.from_user.id))
    conn.commit()

    await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)
    await bot.send_message(chat_id=callback_query.from_user.id, text=f"Аккаунт успешно изменён!",reply_markup=get_start_menu(user_id=callback_query.from_user.id))


