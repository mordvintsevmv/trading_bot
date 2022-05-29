from main import bot, dp
from aiogram.types import Message
from bot.keyboards.start_menu_keyboard import get_start_menu
from aiogram.dispatcher import FSMContext
from aiogram import types
from config.personal_data import ADMIN_ID
from aiogram.dispatcher.filters import Command
import asyncio
import aioschedule
from trading.strategy.ema_adx_macd import start_ema_adx_macd
import sqlite3 as sl

'''
    Тут описаны все хендлеры с основными командами бота
'''

'''
    Отправялет сообщение администратору (мне), что бот запущен
'''


async def start(dp):
    await bot.send_message(chat_id=ADMIN_ID, text="Бот запущен", reply_markup=get_start_menu(ADMIN_ID))
    asyncio.create_task(schedule_ema_adx_macd())


async def schedule_ema_adx_macd():
    aioschedule.every(15).minutes.do(start_ema_adx_macd)

    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


'''
    Выводит приветственный текст при вводе команды /start
'''


@dp.message_handler(Command("start"))
async def show_menu(message: Message):
    await message.answer("Добро пожаловать в торговый бот!", reply_markup=get_start_menu(message.from_user.id))

    conn = sl.connect("db/users.db")
    cur = conn.cursor()

    info = cur.execute('SELECT * FROM USER WHERE id=?', (message.from_user.id,))
    if info.fetchone() is None:
        user = (
            message.from_user.id, message.from_user.first_name, message.from_user.last_name, message.from_user.username,
            "",
            "", "")
        cur.execute("INSERT INTO USER VALUES(?, ?, ?, ?, ?, ?, ?);", user)
        conn.commit()


'''
    Выводит приветственный текст при вводе текста
'''


@dp.message_handler(text="Приветствие")
async def hello_message(message: Message):
    await message.answer(f"Привет, {message.from_user.first_name}! Это торговый бот. Пока я мало что умею, но я хороший!")


'''
    Отменяет любое состояние и возвращать в начальное меню
'''


@dp.message_handler(state="*", text="Отмена")
async def cancel(message: types.Message, state: FSMContext):
    await message.answer("Действие было отменено!", reply_markup=get_start_menu(message.from_user.id))
    await state.reset_state()
