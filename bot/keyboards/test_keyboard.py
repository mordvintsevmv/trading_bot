from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

"""
    Пока что тестовая клавиатура
"""

tink_menu = InlineKeyboardMarkup(
    inline_keyboard=
    [
        [
            InlineKeyboardButton(text="Открыть Тинькофф Инвестиции", callback_data= "", url='https://www.tinkoff.ru/invest/'),
        ],
        [
            InlineKeyboardButton(text="Ввести Токен", callback_data="buy:apple:5"),
        ],
    ]
)