from main import dp
from aiogram.types import Message
from aiogram.dispatcher.filters import Text
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

'''
    Выводит варианты алготрейдинга
'''


@dp.message_handler(Text(contains="Торговые стратегии", ignore_case=True))
async def algo_trade(message: Message):
    await message.answer(f"Выберите торговую стратегию:\n")

    str1_keyboard = InlineKeyboardMarkup()
    str1_keyboard.add(InlineKeyboardButton(text="Торговля", callback_data="str1:list"))
    str1_keyboard.add(
        InlineKeyboardButton(text="Добавить бумагу в стратегию", callback_data="str1:settings:add:start"))
    str1_keyboard.add(
        InlineKeyboardButton(text="Удалить бумагу из стратегии", callback_data="str1:settings:delete:start"))

    await message.answer(f"EMA + ADX + MACD\n", reply_markup=str1_keyboard)
