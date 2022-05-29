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
from trading.add_money_sandbox import add_money_sandbox

"""

    Тут представлены все хэндлеры, которые отвечают за добавление токена

"""



"""
    Первый хэндлер, который запускает состояние продажи
"""

@dp.message_handler(state="*", text="Пополнить счёт")
async def choose_account(message: Message):

    conn = sl.connect("db/users.db")
    cur = conn.cursor()

    token = cur.execute('SELECT token FROM USER WHERE id = ? ', (message.from_user.id,)).fetchone()[0]

    os.environ.setdefault('INVEST_TOKEN', str(token))

    choose_account = InlineKeyboardMarkup()
    choose_account.add(InlineKeyboardButton(text=f"1000₽", callback_data=f"sandbox:add:1000:rub"))
    choose_account.add(InlineKeyboardButton(text=f"1000$", callback_data=f"sandbox:add:1000:usd"))
    choose_account.add(InlineKeyboardButton(text=f"1000€", callback_data=f"sandbox:add:1000:eur"))

    await message.answer("Выберите сумму пополнения:", reply_markup=choose_account)

"""
    Второй хендлер, который испольняется в состоянии s_wait_figi
"""

@dp.callback_query_handler(lambda c: c.data and c.data.startswith("sandbox:add"))
async def account_finish(callback_query):

    data = callback_query.data.split(":")

    sum = data[2]
    cur = data[3]

    add_money_sandbox(user_id=callback_query.from_user.id, sum=sum, cur=cur)


