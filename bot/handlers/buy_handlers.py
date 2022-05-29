from main import dp
from aiogram.types import Message
from bot.keyboards.start_menu_keyboard import get_start_menu
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup
from aiogram import types
from trading.trade_help import share_lot_figi
from trading.get_by_figi import sfb_name_by_figi
from trading.trade_help import in_shares
from trading.get_info import get_price_figi
from trading.place_order import buy_sfb

"""

    Тут представлены все хэндлеры, которые отвечают за покупку бумаг

"""


"""
    Создаём три состояния FSM
"""


class BuyOrder(StatesGroup):
    b_wait_figi = State()
    b_wait_quantity = State()
    b_wait_price = State()


"""
    Первый хэндлер, который запускает состояние покупки
"""

@dp.message_handler(text="Купить")
async def b_choose_figi(message: Message, state: FSMContext):

    # Создадим клавиатуру с примерами FIGI
    figi_keyboard = ReplyKeyboardMarkup()

    # Покажем информацию о выбранных бумагах
    await message.answer(
        f"BBG004730ZJ9 - {sfb_name_by_figi('BBG004730ZJ9', user_id=message.from_user.id)}\n"
        f"BBG0014PFYM2 - {sfb_name_by_figi('BBG0014PFYM2', user_id=message.from_user.id)}\n"
        f"BBG000K3STR7 - {sfb_name_by_figi('BBG000K3STR7', user_id=message.from_user.id)}\n"
        f"BBG001M2SC01 - {sfb_name_by_figi('BBG001M2SC01', user_id=message.from_user.id)}\n"
        )

    # Добваим значения в клавиатуру
    figi_keyboard.add(f"BBG004730ZJ9")
    figi_keyboard.add(f"BBG0014PFYM2")
    figi_keyboard.add(f"BBG000K3STR7")
    figi_keyboard.add(f"BBG001M2SC01")
    figi_keyboard.add(f"Отмена")

    # Включим клавиатуру
    await message.answer("Выберите figi вашей бумаги (или введите сами):", reply_markup=figi_keyboard)

    # Перейдём в следующее состояние
    await BuyOrder.b_wait_figi.set()


"""
    Второй хэндлер, который находится в состоянии b_wait_figi
"""


@dp.message_handler(state=BuyOrder.b_wait_figi, content_types=types.ContentTypes.TEXT)
async def b_choose_quantity(message: Message, state: FSMContext):

    # Проверяем, существует ли такая акция
    if in_shares(message.text, user_id=message.from_user.id):

        # Создаём клавиатуру с примерами лотов
        lot_keyboard = ReplyKeyboardMarkup()
        lot_keyboard.add(f"1")
        lot_keyboard.add(f"2")
        lot_keyboard.add(f"3")
        lot_keyboard.add(f"4")
        lot_keyboard.add(f"Отмена")

        # Аключаем клавиатуру
        await message.answer(f"Бумаг в лоте: {share_lot_figi(message.text, user_id=message.from_user.id)}")

        price = get_price_figi(message.text, user_id=message.from_user.id)

        # Выведем всю информации о выбранной бумаге
        await message.answer(f"Средняя стоимость бумаги: {round(price, 6)}")
        await message.answer(f"Примерная стоимость лота: {round(price*share_lot_figi(message.text, user_id=message.from_user.id), 6)}")
        await message.answer("Укажите количество лотов для покупки:", reply_markup=lot_keyboard)

        # Запишем в память
        await state.update_data(b_chosen_figi=message.text)

        # Перейдём в следующее состояние
        await BuyOrder.b_wait_quantity.set()
        return

    # В случае ошибки повторим запрос
    else:
        await message.answer("Введите коррекнтый FIGI!")
        return


"""
    Третий хэндлер, который находится в состоянии b_wait_quantity
"""


@dp.message_handler(state=BuyOrder.b_wait_quantity)
async def b_choose_price(message: Message, state: FSMContext):

    # Проверяем корректность введёных данных
    if int(message.text) > 0:

        # Запишем в память
        await state.update_data(b_chosen_quantity=message.text)

        user_data = await state.get_data()
        price = get_price_figi(user_data['b_chosen_figi'], user_id=message.from_user.id)

        # Создадим клавиатуру с примерами цены на бумагу
        price_keyboard = ReplyKeyboardMarkup()

        price_keyboard.add(f"{round(price * 1.02,5)}")
        price_keyboard.add(f"{round(price * 1.01,5)}")
        price_keyboard.add(f"{round(price * 1.00,5)}")
        price_keyboard.add(f"{round(price * 0.99,5)}")
        price_keyboard.add(f"{round(price * 0.98,5)}")
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
    if float(message.text) == 0.0:
        # Продадим бумаги и выведем cообщение
        user_data = await state.get_data()
        await message.answer(
            f"Купить акции {user_data['b_chosen_figi']} в количестве {user_data['b_chosen_quantity']} по лучшей цене.\n",
            reply_markup=get_start_menu(message.from_user.id))
        buy_sfb(figi=user_data['b_chosen_figi'], price=0.0,
                quantity_lots=int(user_data['b_chosen_quantity']), user_id=message.from_user.id)
        await state.finish()
    elif price * 1.20 > float(message.text) > price * 0.80:

        # Продадим бумаги и выведем сообщение
        user_data = await state.get_data()
        await message.answer(
            f"Купить акции {user_data['b_chosen_figi']} в количестве {user_data['b_chosen_quantity']} по цене {message.text}.\n",reply_markup=get_start_menu(message.from_user.id))
        buy_sfb(figi = user_data['b_chosen_figi'], price = float(message.text), quantity_lots = int(user_data['b_chosen_quantity']), user_id=message.from_user.id, via="bot")
        await state.finish()

    # В случае ошибки повторим запрос
    else:
        await message.answer("Введите корректную цену!")
