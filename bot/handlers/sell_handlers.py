from main import dp
from aiogram.types import Message
from bot.keyboards.start_menu_keyboard import get_start_menu
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from trading.get_info import get_lots, get_price
from aiogram import types
from aiogram.types import ReplyKeyboardMarkup
from tinkoff.invest import Client
from trading.trade_help import in_portf, share_lot_figi
from config.personal_data import get_account, get_token, get_account_type
from trading.place_order import sell_sfb

"""

    Тут представлены все хэндлеры, которые отвечают за продажу бумаг

"""

"""
    Создаём три состояния FSM
"""


class SellOrder(StatesGroup):
    s_wait_figi = State()
    s_wait_quantity = State()
    s_wait_price = State()


"""
    Первый хэндлер, который запускает состояние продажи
"""


@dp.message_handler(state="*", text="Продать")
async def s_choose_figi(message: Message):
    emprty_portf = True

    # Создадим клавиатуру, которая покажет доступные FIGI для продажи
    figi_keyboard = ReplyKeyboardMarkup()

    # Вставим в клавиатуру все значения из нашего портфеля
    with Client(get_token(message.from_user.id)) as client:
        if get_account_type(message.from_user.id) == "sandbox":
            portf = client.sandbox.get_sandbox_portfolio(account_id=get_account(message.from_user.id))
        else:
            portf = client.operations.get_portfolio(account_id=get_account(message.from_user.id))
        for i in portf.positions:
            if i.instrument_type != "currency":
                figi_keyboard.add(i.figi)
                emprty_portf = False
        figi_keyboard.add("Отмена")

    if emprty_portf:
        await message.answer("У Вас нет бумаг на продажу!", reply_markup=get_start_menu(message.from_user.id))
        return

    # Включаем клавиатуру
    await message.answer("Введите figi вашей бумаги:", reply_markup=figi_keyboard)

    # Переводим в состояние ожидания ввода FIGI
    await SellOrder.s_wait_figi.set()


"""
    Второй хендлер, который испольняется в состоянии s_wait_figi
"""


@dp.message_handler(state=SellOrder.s_wait_figi, content_types=types.ContentTypes.TEXT)
async def s_choose_quantity(message: Message, state: FSMContext):
    # Используем функцию, которая проверит, существует ли такая акция в портфеле
    if in_portf(message.text, user_id=message.from_user.id):

        # Создадим клавиатуру, которая выведет досутпное количество лотов
        lot_keyboard = ReplyKeyboardMarkup()
        for i in range(get_lots(message.text, user_id=message.from_user.id)):
            lot_keyboard.add(f"{i + 1}")
        lot_keyboard.add(f"Отмена")

        # Включим клавиатуру
        await message.answer("Укажите количество лотов для продажи:", reply_markup=lot_keyboard)

        # Запишем данные о FIGI в память
        await state.update_data(s_chosen_figi=message.text)

        # Перейдём в следующее состояние
        await SellOrder.s_wait_quantity.set()
        return

    # Если введено неверное значение FIGI, то повторим запрос
    else:
        await message.answer("Пожалуйста, выберите из списка!")
        return


"""
    Третий хендлер, который испольняется в состоянии s_wait_quantity
"""


@dp.message_handler(state=SellOrder.s_wait_quantity)
async def s_choose_price(message: Message, state: FSMContext):
    # Получим цену бумаги
    user_data = await state.get_data()
    price = get_price(user_data['s_chosen_figi'], user_id=message.from_user.id)

    # Проверяем, есть ли такое количество лотов в портфеле
    if get_lots(user_data['s_chosen_figi'], user_id=message.from_user.id) >= int(message.text) > 0:

        # Создаём клавиатуру с ценами
        # Для удобства было добавлено несколько цен на 1% и 2% меньше/больше текущей
        # При этом также можно ввести свою цену
        price_keyboard = ReplyKeyboardMarkup()

        price_keyboard.add(f"{round(price * 1.02, 5)}")
        price_keyboard.add(f"{round(price * 1.01, 5)}")
        price_keyboard.add(f"{round(price * 1.00, 6)}")
        price_keyboard.add(f"{round(price * 0.99, 5)}")
        price_keyboard.add(f"{round(price * 0.98, 5)}")
        price_keyboard.add(f"Отмена")

        # Включаем клавиатуру
        await message.answer(f"Текущая стоимость бумаги: {price}", reply_markup=price_keyboard)
        await message.answer("Укажите цену за бумагу (или напишите свою):")

        # Запишем данные о количестве в память
        await state.update_data(s_chosen_quantity=message.text)

        # Переходим в следующее состояние
        await SellOrder.s_wait_price.set()
        return

    # В случае ошибки повторяем запрос
    else:
        await message.answer(f"Введите доступное число лотов!")
        return


"""
    Последний хендлер, который испольняется в состоянии s_wait_price
"""


@dp.message_handler(state=SellOrder.s_wait_price)
async def s_finish(message: types.Message, state: FSMContext):
    # Получаем цену бумаги
    user_data = await state.get_data()
    price = get_price(user_data['s_chosen_figi'], user_id=message.from_user.id)

    # Проверяем, что цена находится в разумных пределах
    if float(message.text) == 0.0:
        # Продаём бумаги и выводим сообщение об этом
        await message.answer(
            f"Продать акции {user_data['s_chosen_figi']} в количестве {user_data['s_chosen_quantity']} по лучшей цене.\n",
            reply_markup=get_start_menu(message.from_user.id))
        sell_sfb(figi=user_data['s_chosen_figi'], price=0.0,
                 quantity_lots=int(user_data['s_chosen_quantity']), user_id=message.from_user.id)
        await state.finish()
        return
    elif (price * 1.20) > float(message.text) > (price * 0.80):

        # Продаём бумаги и выводим сообщение об этом
        await message.answer(
            f"Продать акции {user_data['s_chosen_figi']} в количесвте {user_data['s_chosen_quantity']} по цене {message.text}.\n"
            f"Суммарно на {round(float(user_data['s_chosen_quantity']) * share_lot_figi(user_data['s_chosen_figi'], user_id=message.from_user.id) * float(message.text), 3)}",
            reply_markup=get_start_menu(message.from_user.id))
        sell_sfb(figi=user_data['s_chosen_figi'], price=float(message.text),
                 quantity_lots=int(user_data['s_chosen_quantity']), user_id=message.from_user.id, via="bot")
        await state.finish()
        return

    # В случае ошибки повторяем запрос
    else:
        await message.answer(f"Введите корректную стоимость!")
        return
