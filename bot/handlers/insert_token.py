from main import dp
from aiogram.types import Message
from bot.keyboards.start_menu_keyboard import get_start_menu
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types
from aiogram.types import ReplyKeyboardRemove
import sqlite3 as sl
import bcrypt



"""

    Тут представлены все хэндлеры, которые отвечают за добавление токена

"""


"""
    Создаём три состояния FSM
"""

class TokenWaiting(StatesGroup):
    wait_token = State()



"""
    Первый хэндлер, который запускает состояние продажи
"""

@dp.message_handler(state="*", text="Изменить Токен")
async def choose_token(message: Message, state: FSMContext):

    await message.answer("Введите токен!", reply_markup=ReplyKeyboardRemove())

    await TokenWaiting.next()

"""
    Второй хендлер, который испольняется в состоянии s_wait_figi
"""

@dp.message_handler(state=TokenWaiting.wait_token, content_types=types.ContentTypes.TEXT)
async def token_finish(message: Message, state: FSMContext):

    conn = sl.connect("db/users.db")
    cur = conn.cursor()

    cur.execute('UPDATE USER SET token = ? WHERE id = ?;', (message.text,message.from_user.id))
    conn.commit()

    await message.answer("Ваш токен добавлен!", reply_markup=get_start_menu(message.from_user.id))

    await state.finish()