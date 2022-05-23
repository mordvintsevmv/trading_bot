from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

"""
    Клавиатура стартового меню
"""

start_menu = ReplyKeyboardMarkup(
    keyboard = [
        [
            KeyboardButton(text="Приветствие"),
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