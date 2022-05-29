from aiogram import Bot, Dispatcher, executor
from config.personal_data import BOT_TOKEN
import asyncio
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from db.create_tables import create_tables
import sqlite3 as sl
from trading.trade_help import to_quotation

from tinkoff.invest import Client, Quotation, CandleInterval
from config import personal_data
from trading.trade_help import total_quantity
from datetime import datetime, timedelta
import pandas as pd
from config.personal_data import get_token, get_account, get_account_type

loop = asyncio.get_event_loop()
bot = Bot(BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot, loop=loop, storage=MemoryStorage())



if __name__ == "__main__":

    from main import dp
    from bot.handlers.bot_handlers import start

    create_tables()

    executor.start_polling(dp, on_startup=start)

