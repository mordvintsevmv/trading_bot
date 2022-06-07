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
from config.crypto_rsa import encrypt
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

    token = get_token(message.from_user.id)

    choose_account = InlineKeyboardMarkup()

    with Client(str(token)) as client:
        acc = client.users.get_accounts()
        acc_sand = client.sandbox.get_sandbox_accounts()
        for i in acc.accounts:
            if i.name != "Инвесткопилка":
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

    conn_users = sl.connect("db/users.db")
    cur_users = conn_users.cursor()
    cur_users.execute('UPDATE USER SET account_id = ?, account_type = ? WHERE user_id = ?;', (account_id, account_type, callback_query.from_user.id))
    conn_users.commit()


    conn_accounts = sl.connect("db/accounts.db")
    cur_accounts = conn_accounts.cursor()

    token = encrypt(get_token(callback_query.from_user.id))

    info = cur_accounts.execute('SELECT * FROM ACCOUNTS WHERE user_id = ? and account_id = ?', (callback_query.from_user.id, account_id)).fetchone()

    if info is None:
        cur_accounts.execute('INSERT INTO ACCOUNTS (user_id, token, account_id, account_type) VALUES (?,?,?,?);',
                      (callback_query.from_user.id, token, account_id, account_type))
        conn_accounts.commit()

    await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)
    await bot.send_message(chat_id=callback_query.from_user.id, text=f"Аккаунт успешно изменён!",reply_markup=get_start_menu(user_id=callback_query.from_user.id))


