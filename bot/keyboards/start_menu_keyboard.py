from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from config.personal_data import get_account_type

"""
    Клавиатура стартового меню
"""
def get_start_menu(user_id):
    if get_account_type(user_id) == "sandbox":
        start_menu = ReplyKeyboardMarkup(
            keyboard = [
                [
                    KeyboardButton(text="Приветствие"),
                ],
                [
                    KeyboardButton(text="Пополнить счёт"),
                ],
                [
                    KeyboardButton(text="Изменить Токен"),
                    KeyboardButton(text="Изменить Аккаунт"),
                ],
                [
                    KeyboardButton(text="Баланс"),
                    KeyboardButton(text="Бумаги"),
                ],
                [
                    KeyboardButton(text="Статистика"),
                ],
                [
                    KeyboardButton(text="Открытые ордера"),
                ],
                [
                    KeyboardButton(text="Продать"),
                    KeyboardButton(text="Купить"),
                ],
                [
                    KeyboardButton(text="Торговые стратегии"),
                ],

            ],
            resize_keyboard=True
        )
    else:
        start_menu = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="Приветствие"),
                ],
                [
                    KeyboardButton(text="Открыть песочницу"),
                    KeyboardButton(text="Закрыть песочницу"),

                ],
                [
                    KeyboardButton(text="Изменить Токен"),
                    KeyboardButton(text="Изменить Аккаунт"),
                ],
                [
                    KeyboardButton(text="Баланс"),
                    KeyboardButton(text="Бумаги"),
                ],
                [
                    KeyboardButton(text="Статистика"),
                ],
                [
                    KeyboardButton(text="Открытые ордера"),
                ],
                [
                    KeyboardButton(text="Продать"),
                    KeyboardButton(text="Купить"),
                ],
                [
                    KeyboardButton(text="Торговые стратегии"),
                ],

            ],
            resize_keyboard=True
        )
    return start_menu