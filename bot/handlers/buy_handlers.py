from main import bot
from config.personal_data import get_account
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from trading.get_account_info import get_currency_sing
from main import dp
from aiogram.types import Message
from bot.keyboards.start_menu_keyboard import get_start_menu
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup
from aiogram import types
from trading.trade_help import in_lot_figi
from trading.trade_help import get_price_figi
from trading.place_order import buy_order
from trading.check_av import check_time
from config.personal_data import get_account_type
from trading.get_securities import get_security_list

"""

    Тут представлены все хэндлеры, которые отвечают за продажу бумаг

"""

"""
    Создаём три состояния FSM
"""


class SearchSFB(StatesGroup):
    wait_sfb = State()


class BuyOrder(StatesGroup):
    b_wait_figi = State()
    b_wait_quantity = State()
    b_wait_price = State()


"""
    Начало поиска бумаг
"""


@dp.message_handler(text="Купить")
async def start_buy(message):
    await bot.send_message(chat_id=message.from_user.id, text="Введите название бумаги или FIGI:")
    await SearchSFB.wait_sfb.set()


"""
    Поиск бумаг на покупку
"""


@dp.message_handler(state=SearchSFB.wait_sfb)
async def search_security_buy(message: Message, state: FSMContext):
    security_list = get_security_list(user_id=message.from_user.id, name=message.text)
    if len(security_list) != 0:
        for security in security_list:

            choose_share_keyboard = InlineKeyboardMarkup()
            choose_share_keyboard.add(
                InlineKeyboardButton(text=f"Купить", callback_data=f"buy:figi:{security.figi}"))

            await message.answer(
                text=
                f"🧾<b>{security.name}</b>\n"
                f"FIGI: {security.figi}\n\n"
                f"Бумаг в лоте: {security.lot}\n"
                f"Средняя цена бумаги: {round(get_price_figi(user_id=message.from_user.id, figi=security.figi), 4)}{get_currency_sing(security.currency)}\n"
                f"Итого стоимость: {round(security.lot * get_price_figi(user_id=message.from_user.id, figi=security.figi), 4)}{get_currency_sing(security.currency)}\n"
                , reply_markup=choose_share_keyboard)

            await state.finish()
    else:
        await bot.send_message(chat_id=message.from_user.id, text=f"Такой бумаги нет!")
        await bot.send_message(chat_id=message.from_user.id, text=f"Повторите ввод или напишите 'Отмена':")
        return 0


"""
    Выбор количества лотов
"""


@dp.callback_query_handler(lambda c: c.data and c.data.startswith("buy:figi"))
async def b_choose_quantity(callback_query, state: FSMContext):

    data = callback_query.data.split(":")
    figi = data[2]

    # Проверяем, доступна ли она сейчас для покупки
    if check_time(user_id=callback_query.from_user.id, figi=figi)[0] or get_account_type(
            user_id=callback_query.from_user.id) == "sandbox":

        # Запишем в память
        await state.update_data(b_chosen_figi=figi)

        # Создаём клавиатуру с примерами лотов
        lot_keyboard = ReplyKeyboardMarkup()
        lot_keyboard.add(f"1")
        lot_keyboard.add(f"2")
        lot_keyboard.add(f"3")
        lot_keyboard.add(f"4")
        lot_keyboard.add(f"Отмена")

        # Выведем всю информации о выбранной бумаге
        price = get_price_figi(figi=figi, user_id=callback_query.from_user.id)

        await bot.send_message(chat_id=callback_query.from_user.id,
                               text=f"Бумаг в лоте: {in_lot_figi(figi=figi, user_id=callback_query.from_user.id)}\n"
                                    f"Средняя стоимость бумаги: {round(price, 6)}\n"
                                    f"Примерная стоимость лота: {round(price * in_lot_figi(figi=figi, user_id=callback_query.from_user.id), 6)}")

        await bot.send_message(chat_id=callback_query.from_user.id, text="Укажите количество лотов для покупки:",
                               reply_markup=lot_keyboard)

        # Перейдём в следующее состояние
        await BuyOrder.b_wait_quantity.set()
        return
    else:
        await state.reset_state()
        await bot.send_message(chat_id=callback_query.from_user.id, text="Торги ещё не начались!")
        await bot.send_message(chat_id=callback_query.from_user.id,
                               text=check_time(user_id=callback_query.from_user.id, figi=figi)[1],
                               reply_markup=get_start_menu(callback_query.from_user.id))


"""
    Третий хэндлер, который находится в состоянии b_wait_quantity
"""


@dp.message_handler(state=BuyOrder.b_wait_quantity)
async def b_choose_price(message: Message, state: FSMContext):
    # Проверяем корректность введённых данных
    if int(message.text) > 0:

        # Запишем в память
        await state.update_data(b_chosen_quantity=message.text)

        user_data = await state.get_data()
        price = get_price_figi(user_data['b_chosen_figi'], user_id=message.from_user.id)

        # Создадим клавиатуру с примерами цены на бумагу
        price_keyboard = ReplyKeyboardMarkup()

        price_keyboard.add(f"Лучшая цена")
        price_keyboard.add(f"{round(price * 1.02, 5)}")
        price_keyboard.add(f"{round(price * 1.01, 5)}")
        price_keyboard.add(f"{round(price * 1.00, 5)}")
        price_keyboard.add(f"{round(price * 0.99, 5)}")
        price_keyboard.add(f"{round(price * 0.98, 5)}")
        price_keyboard.add(f"Отмена")

        # Включим клавиатуру
        await message.answer("Укажите цену за бумагу:", reply_markup=price_keyboard)
        await BuyOrder.b_wait_price.set()

    # В случае ошибки повторим запрос
    else:
        await message.answer("Введите корректное число лотов!")


"""
    Последний хэндлер, который покупает бумаги
"""


@dp.message_handler(state=BuyOrder.b_wait_price)
async def b_finish(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    price = get_price_figi(user_data['b_chosen_figi'], user_id=message.from_user.id)

    # Проверяем, что цена находится в разумных границах
    if message.text == "Лучшая цена":
        await state.finish()
        # Продадим бумаги и выведем сообщение
        await message.answer(
            f"Купить акции {user_data['b_chosen_figi']} в количестве {user_data['b_chosen_quantity']} по лучшей цене.\n",
            reply_markup=get_start_menu(message.from_user.id))
        buy_order(figi=user_data['b_chosen_figi'], price=0.0,
                  quantity_lots=int(user_data['b_chosen_quantity']), user_id=message.from_user.id)
    elif price * 1.20 > float(message.text) > price * 0.80:
        await state.finish()
        # Продадим бумаги и выведем сообщение
        await message.answer(
            f"Купить акции {user_data['b_chosen_figi']} в количестве {user_data['b_chosen_quantity']} по цене {message.text}.\n",
            reply_markup=get_start_menu(message.from_user.id))
        buy_order(figi=user_data['b_chosen_figi'], price=float(message.text),
                  quantity_lots=int(user_data['b_chosen_quantity']), user_id=message.from_user.id, via="bot", account_id=get_account(user_id=user_data))
    # В случае ошибки повторим запрос
    else:
        await message.answer("Введите корректную цену!")
        return
