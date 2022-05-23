from main import dp, bot
from aiogram.types import Message
from aiogram.dispatcher.filters import Text
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from trading.strategy.ema_adx_macd import stat_ema_adx_macd
import pandas as pd

str1_conf = InlineKeyboardMarkup(
    inline_keyboard =
        [
            [
                InlineKeyboardButton(text=f"-1", callback_data=f"-1"),
                InlineKeyboardButton(text=f"-0.5", callback_data=f"-0.5"),
                InlineKeyboardButton(text=f"-0.05", callback_data=f"-0.05"),
                InlineKeyboardButton(text=f"+0.05", callback_data=f"+0.05"),
                InlineKeyboardButton(text=f"+0.5", callback_data=f"+0.5"),
                InlineKeyboardButton(text=f"+1", callback_data=f"+1"),
            ]
        ],
)
