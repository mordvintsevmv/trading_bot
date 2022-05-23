from main import dp, bot
from aiogram.types import Message
from aiogram.dispatcher.filters import Text
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from trading.strategy.ema_adx_macd import stat_ema_adx_macd
from trading.get_by_figi import sfb_name_by_figi

'''
    Выводит варианты алготрейдинга
'''

days = 2
week = 4


@dp.message_handler(Text(contains="Торговые стратегии", ignore_case=True))
async def algo_trade(message: Message):
    await message.answer(f"Выберите торговую стратегию:\n")

    ema_adx_macd_keyboard = get_str1_keyboard()

    await message.answer(f"EMA + ADX + MACD\n", reply_markup=ema_adx_macd_keyboard)


'''
    Информация по Стратегии 1
'''


@dp.callback_query_handler(lambda c: c.data and c.data.startswith("ema_adx_macd_stat_"))
async def ema_adx_macd_stat(callback_query):
    FIGI = callback_query.data[18:]

    await bot.send_message(chat_id=callback_query.from_user.id, text=f"<b>{sfb_name_by_figi(FIGI)}</b>")
    await bot.send_message(chat_id=callback_query.from_user.id, text=f"15-минутный грфик:")
    stat_15 = stat_ema_adx_macd(figi=FIGI, period=days, hour_graph=False)
    photo_15 = open(f"img/str1/graph/15_min_{FIGI}.png", "rb")
    await bot.send_photo(chat_id=callback_query.from_user.id, photo=photo_15)

    photo_15 = open(f"img/str1/ind/15_min_{FIGI}.png", "rb")
    await bot.send_photo(chat_id=callback_query.from_user.id, photo=photo_15)

    if stat_15[0]:
        await bot.send_message(chat_id=callback_query.from_user.id, text=f"📈Цена растёт📈\n{stat_15[1]}")
    else:
        await bot.send_message(chat_id=callback_query.from_user.id, text=f"📉Цена падает📉\n{stat_15[1]}")

    await bot.send_message(chat_id=callback_query.from_user.id, text=f"Часовой график:")
    stat_hour = stat_ema_adx_macd(figi=FIGI, period=week, hour_graph=True)
    photo_hour = open(f"img/str1/graph/hour_{FIGI}.png", "rb")
    await bot.send_photo(chat_id=callback_query.from_user.id, photo=photo_hour)

    photo_hour = open(f"img/str1/ind/hour_{FIGI}.png", "rb")
    await bot.send_photo(chat_id=callback_query.from_user.id, photo=photo_hour)

    if stat_hour[0]:
        await bot.send_message(chat_id=callback_query.from_user.id, text=f"📈Цена растёт📈\n{stat_hour[1]}")
    else:
        await bot.send_message(chat_id=callback_query.from_user.id, text=f"📉Цена падает📉\n{stat_hour[1]}")


'''
    Старт Стратегии 1
'''


@dp.callback_query_handler(lambda c: c.data and c.data.startswith("ema_adx_macd_start_"))
async def ema_adx_macd_start(callback_query):
    FIGI = callback_query.data[19:]

    with open('config/str1_status.txt', 'r') as f:
        old_data = f.read()

    new_data = old_data.replace(f'figi:{FIGI};status:False;', f'figi:{FIGI};status:True;')

    with open('config/str1_status.txt', 'w') as f:
        f.write(new_data)

    await bot.send_message(chat_id=callback_query.from_user.id, text=f"Стратегия для бумаг <b>{sfb_name_by_figi(FIGI)}</b> была запущена!")

    ema_adx_macd_keyboard = get_str1_keyboard()
    await bot.edit_message_text(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id, text=callback_query.message.text, reply_markup=ema_adx_macd_keyboard)



'''
    Стоп Стратегии 1
'''


@dp.callback_query_handler(lambda c: c.data and c.data.startswith("ema_adx_macd_stop_"))
async def ema_adx_macd_stop(callback_query):
    FIGI = callback_query.data[18:]

    with open('config/str1_status.txt', 'r') as f:
        old_data = f.read()

    new_data = old_data.replace(f'figi:{FIGI};status:True;', f'figi:{FIGI};status:False;')

    with open('config/str1_status.txt', 'w') as f:
        f.write(new_data)

    await bot.send_message(chat_id=callback_query.from_user.id, text=f"Стратегия для бумаг <b>{sfb_name_by_figi(FIGI)}</b> была остановлена!")

    ema_adx_macd_keyboard = get_str1_keyboard()
    await bot.edit_message_text(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id, text=callback_query.message.text, reply_markup=ema_adx_macd_keyboard)



def get_str1_keyboard():
    str1_status = open("config/str1_status.txt", "r")

    str1_menu = []

    for line in str1_status:
        if line == '\n': continue
        line = line.split(";")
        if line[1][7:] == "True":
            stat_str1_button = InlineKeyboardButton(text=f"Анализ {sfb_name_by_figi(line[0][5:])}",
                                                    callback_data=f"ema_adx_macd_stat_{line[0][5:]}")
            status_str1_button = InlineKeyboardButton(text=f"Остановить торговлю",
                                                      callback_data=f"ema_adx_macd_stop_{line[0][5:]}")
        else:
            stat_str1_button = InlineKeyboardButton(text=f"Анализ {sfb_name_by_figi(line[0][5:])}",
                                                    callback_data=f"ema_adx_macd_stat_{line[0][5:]}")

            status_str1_button = InlineKeyboardButton(text=f"Начать торговлю",
                                                      callback_data=f"ema_adx_macd_start_{line[0][5:]}")

        str1_menu.append([stat_str1_button, status_str1_button])

    str1_status.close()
    ema_adx_macd_keyboard = InlineKeyboardMarkup(
        inline_keyboard=
        str1_menu,
    )

    return ema_adx_macd_keyboard
