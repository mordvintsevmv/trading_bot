from main import bot, dp
from aiogram.types import Message
from bot.keyboards.start_menu_keyboard import start_menu
from aiogram.dispatcher import FSMContext
from aiogram import types
#from config.personal_data import ADMIN_ID
from aiogram.dispatcher.filters import Command
import asyncio
import aioschedule
from trading.strategy.ema_adx_macd import start_ema_adx_macd

'''
    Тут описаны все хендлеры с основными командами бота
'''



'''
    Отправялет сообщение администратору (мне), что бот запущен
'''


async def start(dp):
    #await bot.send_message(chat_id=ADMIN_ID, text="Бот запущен", reply_markup=start_menu)
    asyncio.create_task(schedule_ema_adx_macd())


async def schedule_ema_adx_macd():
    aioschedule.every().minute.do(start_ema_adx_macd)

    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)



'''
    Выводит приветственный текст при вводе команды /start
'''


@dp.message_handler(Command("start"))
async def show_menu(message: Message):
    await message.answer("Добро пожаловать в торговый бот!", reply_markup=start_menu)


'''
    Выводит приветственный текст при вводе текста
'''

@dp.message_handler(text="Приветствие")
async def hello_message(message: Message):
    await message.answer("Всем привет! Это торговый бот. Пока я мало что умею, но я хороший!")


'''
    Отменяет любое состояние и возвращать в начальное меню
'''

@dp.message_handler(state="*", text="Отмена")
async def cancel(message: types.Message, state: FSMContext):
    await message.answer("Действие было отменено!", reply_markup=start_menu)
    await state.reset_state()



