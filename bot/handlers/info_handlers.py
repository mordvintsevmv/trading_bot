from trading.get_info import get_all_stat, get_my_order, get_all_currency, get_all_shares
from main import dp, bot
from aiogram.types import Message
from aiogram.dispatcher.filters import Text
from trading.get_by_figi import sfb_name_by_figi
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from trading.place_order import cancel_order
from config.personal_data import get_account_type

"""

    Здесь собраны все хендлеры, которые отвечают за вывод информации о счёте

"""

"""

    Баланс

"""


@dp.message_handler(Text(contains="баланс", ignore_case=True))
async def get_balance(message: Message):

    cur_df = get_all_currency(message.from_user.id)

    await message.answer(f"💸<b>Доступная валюта</b>💸")

    for i in cur_df.index:

        if cur_df['currency'][i] == "rub":
            await message.answer(
                f"{round(cur_df['sum'][i], 2)}₽")

        elif cur_df['currency'][i] == "usd":
            await message.answer(
                f"{round(cur_df['sum'][i], 2)}$")

        elif cur_df['currency'][i] == "eur":
            await message.answer(
                f"{round(cur_df['sum'][i], 2)}€")

        else:
            await message.answer(
                f"{round(cur_df['sum'][i], 2)} {cur_df['currency'][i]}")

"""

    Бумаги

"""


@dp.message_handler(Text(contains="бумаги", ignore_case=True))
async def get_share(message: Message):

    sh_df = get_all_shares(message.from_user.id)

    empty_portf = True
    await message.answer(f"💼Ценные бумаги в портфеле💼")

    for i in sh_df.index:

        inst = ""
        name = ""

        if sh_df['instrument'][i] == "share":
            inst = "Акции"
            name = sfb_name_by_figi(sh_df['figi'][i], user_id=message.from_user.id)
            empty_portf = False

        elif sh_df['instrument'][i] == "bond":
            inst = "Бонды"
            name = sfb_name_by_figi(sh_df['figi'][i], user_id=message.from_user.id)
            empty_portf = False

        elif sh_df['instrument'][i] == "etf":
            inst = "ETF"
            name = sfb_name_by_figi(sh_df['figi'][i], user_id=message.from_user.id)
            empty_portf = False

        elif sh_df['instrument'][i] == "currency":
            continue

        elif sh_df['instrument'][i] == "future":
            inst = "Фьючерсы"
            name = sfb_name_by_figi(sh_df['figi'][i], user_id=message.from_user.id)
            empty_portf = False

        if sh_df['exp_yield'][i] >= 0:
            exp_yield = f"Ожидаемый доход: {round(sh_df['exp_yield'][i], 2)}₽"
        else:
            exp_yield = f"Ожидаемая убыль: {round(sh_df['exp_yield'][i], 2)}₽"

        await message.answer(
            f"🧾<b>{inst} {name}</b>\n"
            f"FIGI: {sh_df['figi'][i]}\n\n"
            f"Лотов: {int(sh_df['lots'][i])}\n"
            f"Всего: {round(sh_df['quantity'][i], 2)}\n\n"
            f"Средняя цена: {sh_df['average_price'][i]}\n"
            f"Средняя цена FIFO: {sh_df['average_price_fifo'][i]}\n"
            f"Текущая цена: {round(sh_df['current_price'][i], 6)}\n\n"
            f"НКД: {sh_df['nkd'][i]}\n"
            f"{exp_yield}\n"
        )

    if empty_portf:
        await message.answer(f"У Вас нет ценных бумаг в портфеле!")


"""

    Статистика по счёту

"""


@dp.message_handler(Text(contains="статистика", ignore_case=True))
async def get_stat(message: Message):
    await message.answer(f"📈<b>Статистика по счёту</b>📉 ")

    stat = get_all_stat(message.from_user.id)

    # Посчитаем сумму всех бумаг
    sum = stat['sum_total'][0]

    # Переведём доход/убыток из проценты в рубли
    dif = round(sum - (sum / (100 + stat['exp_yield'][0])) * 100, 2)

    if dif >= 0:
        dif_text = f"<b>Прибль</b>: {dif}₽ ({stat['exp_yield'][0]}%)"
    else:
        dif_text = f"<b>Убыль</b>: {dif}₽ ({stat['exp_yield'][0]}%)"

    await message.answer(
        f"<b>Акции</b> на сумму: {stat['sum_shares'][0]}₽\n"
        f"<b>Бонды</b> на сумму: {stat['sum_bonds'][0]}₽\n"
        f"<b>ETF</b> на сумму: {stat['sum_etf'][0]}₽\n"
        f"<b>Валюта</b> на сумму: {stat['sum_curr'][0]}₽\n"
        f"<b>Фьючерсы</b> на сумму: {stat['sum_fut'][0]}₽\n\n"
        f"<b>Итого</b>: {round(sum, 2)}₽\n"
        f"{dif_text}\n"

    )


'''
    Открытые ордера
'''


@dp.message_handler(Text(contains="ордер", ignore_case=True))
async def get_orders(message: Message):
    ord_df = get_my_order(message.from_user.id)

    await message.answer(f"📋Открытые ордера📋")

    for i in ord_df.index:

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=
            [
                [
                    InlineKeyboardButton(text=f"Отменить ордер", callback_data=f"ord_id{ord_df['order_id'][i]}"),
                ]
            ],
        )

        if ord_df['direction'][i] == 2:
            dir = "Продажа"
        else:
            dir = "Покупка"

        if ord_df['currency'][i] == "rub":
            currency = "₽"

        elif ord_df['currency'][i] == "eur":
            currency = "€"

        elif ord_df['currency'][i] == "usd":
            currency = "$"

        else:
            currency = ord_df['currency'][i]

        await message.answer(
            f"✅<b>{dir}</b> бумаг {sfb_name_by_figi(ord_df['figi'][i], message.from_user.id)}\n"
            f"Открыт: {ord_df['order_date'][i]}\n\n"
            f"ID: {ord_df['order_id'][i]}\n\n"
            f"FIGI: {ord_df['figi'][i]}\n\n"
            f"Лотов запрошено: {ord_df['lots_req'][i]}\n"
            f"Лотов исполнено: {ord_df['lots_ex'][i]}\n\n"
            f"Сумма запрошена: {ord_df['sum_req'][i]}{currency}\n"
            f"Сумма исполнено: {ord_df['sum_ex'][i]}{currency}\n\n"
            f"Цена одной акции: {round(ord_df['price_one'][i], 6)}{currency}\n\n"
            f"Комиссия: {round(ord_df['commission'][i], 3)}{currency}\n"
            f"Комиссия сервиса: {round(ord_df['serv_commission'][i], 3)}{currency}\n\n"
            f"Итого: {ord_df['sum_total'][i]}{currency}\n",
            reply_markup=keyboard
        )


'''
    Закртыие ордера по id
'''

@dp.callback_query_handler(lambda c: c.data and c.data.startswith('ord_id'))
async def close_order(callback_query):

    order_id = callback_query.data[6:]

    await cancel_order(order_id, user_id=callback_query.from_user.id)

    await bot.edit_message_text(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id, text="❌Ордер отменён❌")

