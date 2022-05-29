from main import dp, bot
from aiogram.types import Message
from aiogram.dispatcher.filters import Text
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from trading.strategy.ema_adx_macd import stat_ema_adx_macd
from config.personal_data import get_account
import sqlite3 as sl

'''
    Выводит варианты алготрейдинга
'''

days = 2
week = 4


@dp.message_handler(Text(contains="Торговые стратегии", ignore_case=True))
async def algo_trade(message: Message):
    await message.answer(f"Выберите торговую стратегию:\n")

    ema_adx_macd_keyboard = get_str1_keyboard(message.from_user.id)

    await message.answer(f"EMA + ADX + MACD\n", reply_markup=ema_adx_macd_keyboard)


'''
    Информация по Стратегии 1
'''


@dp.callback_query_handler(lambda c: c.data and c.data.startswith("str1:stat"))
async def ema_adx_macd_stat(callback_query):
    data = callback_query.data.split(":")

    user_id = data[3]
    figi = data[4]
    name = data[5]

    await bot.send_message(chat_id=callback_query.from_user.id, text=f"<b>{name}</b>")
    await bot.send_message(chat_id=callback_query.from_user.id, text=f"15-минутный грфик:")
    stat_15 = stat_ema_adx_macd(figi=figi, period=days, hour_graph=False, user_id=user_id)
    photo_15 = open(f"img/str1/graph/15_min_{figi}.png", "rb")
    await bot.send_photo(chat_id=callback_query.from_user.id, photo=photo_15)

    photo_15 = open(f"img/str1/ind/15_min_{figi}.png", "rb")
    await bot.send_photo(chat_id=callback_query.from_user.id, photo=photo_15)

    if stat_15[0]:
        await bot.send_message(chat_id=callback_query.from_user.id, text=f"📈Цена растёт📈\n{stat_15[1]}")
    else:
        await bot.send_message(chat_id=callback_query.from_user.id, text=f"📉Цена падает📉\n{stat_15[1]}")

    await bot.send_message(chat_id=callback_query.from_user.id, text=f"Часовой график:")
    stat_hour = stat_ema_adx_macd(figi=figi, period=week, hour_graph=True, user_id=user_id)
    photo_hour = open(f"img/str1/graph/hour_{figi}.png", "rb")
    await bot.send_photo(chat_id=callback_query.from_user.id, photo=photo_hour)

    photo_hour = open(f"img/str1/ind/hour_{figi}.png", "rb")
    await bot.send_photo(chat_id=callback_query.from_user.id, photo=photo_hour)

    if stat_hour[0]:
        await bot.send_message(chat_id=callback_query.from_user.id, text=f"📈Цена растёт📈\n{stat_hour[1]}")
    else:
        await bot.send_message(chat_id=callback_query.from_user.id, text=f"📉Цена падает📉\n{stat_hour[1]}")


'''
    Старт/Стоп Стратегии 1
'''


@dp.callback_query_handler(lambda c: c.data and c.data.startswith("str1:trade"))
async def ema_adx_macd_str1_trade(callback_query):
    data = callback_query.data.split(":")

    status = data[2]
    user_id = data[3]
    figi = data[4]
    account_id = get_account(user_id=user_id)

    conn = sl.connect("db/str1.db")
    cur = conn.cursor()
    cur.execute("UPDATE CONFIG SET trade_status=? WHERE user_id = ? AND figi = ? AND account_id = ?", (status, user_id, figi, account_id))
    conn.commit()
    await bot.edit_message_text(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id, text=callback_query.message.text, reply_markup=get_str1_keyboard(user_id))



'''
    Старт/Стоп Стратегии 1 уведомления
'''


@dp.callback_query_handler(lambda c: c.data and c.data.startswith("str1:notif"))
async def ema_adx_macd_str1_notif(callback_query):
    data = callback_query.data.split(":")

    status = data[2]
    user_id = data[3]
    figi = data[4]
    account_id = get_account(user_id=user_id)

    conn = sl.connect("db/str1.db")
    cur = conn.cursor()
    cur.execute("UPDATE CONFIG SET notif_status=? WHERE user_id = ? AND figi = ? AND account_id = ?", (status, user_id, figi, account_id))
    conn.commit()
    await bot.edit_message_text(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id, text=callback_query.message.text, reply_markup=get_str1_keyboard(user_id))



def get_str1_keyboard(user_id):

    account_id = get_account(user_id)
    conn = sl.connect("db/str1.db")
    cur = conn.cursor()

    shares = cur.execute('SELECT figi,name,trade_status,notif_status FROM CONFIG WHERE user_id = ? AND account_id = ? ',
                         (user_id, account_id)).fetchall()

    str1_menu = []

    for line in shares:
        stat_str1_button = InlineKeyboardButton(text=f"Анализ {line[1]}",
                                                callback_data=f"str1:stat:show:{user_id}:{line[0]}:{line[1]}")

        if line[2] == "True":
            status_str1_button = InlineKeyboardButton(text=f"⏹",
                                                      callback_data=f"str1:trade:False:{user_id}:{line[0]}")
        else:
            status_str1_button = InlineKeyboardButton(text=f"▶️",
                                                      callback_data=f"str1:trade:True:{user_id}:{line[0]}")

        if line[3] == "True":
            status_notif_button = InlineKeyboardButton(text=f"🔔",
                                                       callback_data=f"str1:notif:False:{user_id}:{line[0]}")
        else:
            status_notif_button = InlineKeyboardButton(text=f"🔕", callback_data=f"str1:notif:True:{user_id}:{line[0]}")

        str1_menu.append([stat_str1_button, status_str1_button, status_notif_button])

    ema_adx_macd_keyboard = InlineKeyboardMarkup(
        inline_keyboard=
        str1_menu,
    )

    return ema_adx_macd_keyboard
