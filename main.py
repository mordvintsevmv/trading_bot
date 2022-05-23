from aiogram import Bot, Dispatcher, executor
from config.personal_data import BOT_TOKEN
import asyncio
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from trading.strategy.ema_adx_macd import analyze_ema_adx_macd
from trading.get_by_figi import sfb_name_by_figi

loop = asyncio.get_event_loop()
bot = Bot(BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot, loop=loop, storage=MemoryStorage())

if __name__ == "__main__":

    from main import dp
    from bot.handlers.bot_handlers import start

    f = open("config/str1_status.txt", "r")

    for line in f:
        if line == '\n':
            continue
        line = line.split(";")
        print(f"Операции по {sfb_name_by_figi(line[0][5:])} за 4 недели:")
        print(analyze_ema_adx_macd(figi=line[0][5:], hour_graph=True))
        analyze_ema_adx_macd(figi=line[0][5:], hour_graph=False)

    f.close()

    executor.start_polling(dp, on_startup=start)
