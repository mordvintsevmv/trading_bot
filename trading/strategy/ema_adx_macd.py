from trading.candles.add_indicators import add_ema, add_macd, add_adx
import matplotlib.pyplot as plt
from trading.candles.get_candles import create_hour_graph, create_15_min_graph
import dataframe_image as dfi
from pandas_style.strategy_1 import color_macd
from math import isnan
from trading.get_by_figi import sfb_incr_by_figi, sfb_name_by_figi
from trading.place_order import sell_sfb, buy_sfb
import pandas as pd
import sqlite3 as sl
from main import bot

'''

    Функция, которая позволяет получить графики бумаг, а также таблицу со значениями индикаторов
    Полученные данные будут использованы в телеграм-боте для визуализации стратегии

'''


def stat_ema_adx_macd(figi, user_id, period=4, hour_graph=True):
    # Создаём график и добавляем индикаторы

    if hour_graph:
        df = create_hour_graph(figi, user_id, week=period, save=False)
    else:
        df = create_15_min_graph(figi, user_id, days=period, save=False)

    df = add_ema(df=df, window=7)
    df = add_ema(df=df, window=21)
    df = add_macd(df)
    df = add_adx(df=df, window=14)

    # Добавляем индикаторы EMA на график для наглядности
    df.plot(x='time_graph', y='close')
    ax = df.plot(x='time_graph', y='close')
    df.plot(ax=ax, x="time_graph", y="ema_7", color='green')
    df.plot(ax=ax, x="time_graph", y="ema_21", color='red')

    price_growth = False
    incr = sfb_incr_by_figi(figi, user_id)
    trend_power = ''

    for i in df.index:

        if i > 0 and (df['ema_7'][i - 1] > df['ema_21'][i - 1]) and (df['ema_7'][i] < df['ema_21'][i]) or (
                i > 0 and (isnan(df['ema_21'][i - 1])) and (df['ema_7'][i] < df['ema_21'][i])):
            plt.arrow(x=i, y=df['ema_7'][i] + incr * 120, dx=0, dy=-incr * 80, width=0.6, color='red',
                      head_length=incr * 15)
        elif i > 0 and (df['ema_7'][i - 1] < df['ema_21'][i - 1]) and (df['ema_7'][i] > df['ema_21'][i]) or (
                i > 0 and (isnan(df['ema_21'][i - 1])) and (df['ema_7'][i] > df['ema_21'][i])):
            plt.arrow(x=i, y=df['ema_7'][i] - incr * 120, dx=0, dy=incr * 80, width=0.6, color='green',
                      head_length=incr * 15)

    if df['ema_7'].iloc[-1] > df['ema_21'].iloc[-1]:
        if df['macd'].iloc[-1] > 0:
            if df['adx'].iloc[-1] > 20:
                price_growth = True

    if hour_graph:
        plt.savefig(f"img/str1/graph/hour_{figi}.png")
    else:
        plt.savefig(f"img/str1/graph/15_min_{figi}.png")

    plt.clf()

    style_df = df[-10:-1].drop(['time', 'open', 'low', 'high', 'orders'], axis=1)
    style_df = style_df.style.apply(color_macd)

    if hour_graph:
        dfi.export(style_df, f"img/str1/ind/hour_{figi}.png")
    else:
        dfi.export(style_df, f"img/str1/ind/15_min_{figi}.png")

    if df['adx'].iloc[-1] < 20:
        trend_power = 'Слабый тренд'
    elif df['adx'].iloc[-1] < 40:
        trend_power = 'Умеренный тренд'
    elif df['adx'].iloc[-1] < 60:
        trend_power = 'Сильный тренд'
    elif df['adx'].iloc[-1] < 80:
        trend_power = 'Очень сильный тренд'
    elif df['adx'].iloc[-1] < 100:
        trend_power = 'Слишком сильный тренд'

    return price_growth, trend_power


'''

    Функция, которая позволяет запускать торговый алгоритм для бумаг, которые имеют фалг True

'''


async def start_ema_adx_macd():

    conn = sl.connect("db/str1.db")
    cur = conn.cursor()

    shares = cur.execute('SELECT user_id, account_id, figi, buy_price, macd_border, adx_border, take_profit, stop_loss, notif_status FROM CONFIG WHERE trade_status = "True" ',).fetchall()

    for line in shares:

        user_id = line[0]
        account_id = line[1]
        figi = line[2]
        buy_price = line[3]
        macd_border = line[4]
        adx_border = line[5]
        take_profit = line[6]
        stop_loss = line[7]
        notif_status = line[8]

        await sell_buy_ema_adx_macd(user_id = user_id, account_id = account_id, figi=figi, buy_price=buy_price,
                                        macd_border=macd_border, adx_border=adx_border,
                                        take_profit=take_profit, stop_loss=stop_loss, notif_status = notif_status)



'''

    Функция, которая анализирует торговые индикаторы и покупает или продаёт бумаги

'''


async def sell_buy_ema_adx_macd(user_id, account_id, figi, notif_status, buy_price=0.0, period=5, macd_border=0.0, adx_border=20.0, take_profit=0.02,
                                stop_loss=0.03):
    # Создаём график и добавляем индикаторы

    df = create_hour_graph(user_id= user_id, figi=figi, week=period, save=False)

    df = add_ema(df=df, window=7)
    df = add_ema(df=df, window=21)
    df = add_macd(df)
    df = add_adx(df=df, window=14)

    macd_count = 0  # консолидируется ли macd

    conn = sl.connect("db/str1.db")
    cur = conn.cursor()

    for i in df.index:

        if i > len(df.index) - 6:
            if 1.12 > df["macd"][i - 1] / df["macd"][i] < 0.88:
                if macd_count < 3:
                    macd_count += 1
            elif macd_count > 0:
                macd_count -= 1

    if buy_price == 0.0:  # Если не было покупки
        if df["macd"].iloc[-1] > macd_border:
            if df["macd"].iloc[-1] < df["macd"].iloc[-2]:  # Если MACD растёт
                if macd_count < 3:  # Если MACD не стоит на месте
                    if df["adx"].iloc[-1] > adx_border:
                        if df["ema_7"].iloc[-1] > df["ema_21"].iloc[-1]:
                            r = buy_sfb(user_id=user_id, figi=figi, price=0, quantity_lots=1, via="str1_auto")
                            await bot.send_message(chat_id=user_id, text=f"Покупка акций {sfb_name_by_figi(figi, user_id)} по цене {r}") if notif_status == "True" else 0
                            cur.execute(
                                "UPDATE CONFIG SET buy_price=? WHERE user_id = ? AND figi = ? AND account_id = ?",
                                (r, user_id, figi, account_id))
                            conn.commit()


    else:  # Если была покупка
        if df["ema_7"].iloc[-1] < df["ema_21"].iloc[-1] or macd_count >= 4 or (
                df["macd"].iloc[-1] / df["macd"].iloc[-1] < 0.955) or (
                buy_price / df["close"].iloc[-1] < 1 - stop_loss) or (
                buy_price / df["close"].iloc[-1] > 1 + take_profit):
            r = sell_sfb(figi=figi, price=0, quantity_lots=1, via="str1_auto")
            await bot.send_message(chat_id=user_id,
                                   text=f"Продажа акций {sfb_name_by_figi(figi, user_id)} по цене {r}") if notif_status == "True" else 0
            cur.execute(
                "UPDATE CONFIG SET buy_price=0.0 WHERE user_id = ? AND figi = ? AND account_id = ?",
                (user_id, figi, account_id))
            conn.commit()
    return 0


'''

    Функция, которая позволяет получить использовать алгоритм на исторических данных.
    Такой способ поможет протестировать стратегию и улучшить её.

'''


def analyze_ema_adx_macd(figi, user_id, period=4, hour_graph=True, macd_border=0, adx_border=20, take_profit=0.02,
                               stop_loss=0.03):
    # Создаём график и добавляем индикаторы

    if hour_graph:
        df = create_hour_graph(figi, user_id=user_id, week=period, save=False)
    else:
        df = create_15_min_graph(figi, user_id=user_id, days=period, save=False)

    df = add_ema(df=df, window=7)
    df = add_ema(df=df, window=21)
    df = add_macd(df)
    df = add_adx(df=df, window=14)

    # Добавляем индикаторы EMA на график для наглядности
    df.plot(x='time_graph', y='close')
    ax = df.plot(x='time_graph', y='close')
    df.plot(ax=ax, x="time_graph", y="ema_7", color='green')
    df.plot(ax=ax, x="time_graph", y="ema_21", color='red')

    buy_flag = False  # Была ли уже покупка
    macd_count = 0  # консолидируется ли macd
    stop = False
    buy_price = 0.0
    incr = sfb_incr_by_figi(user_id=user_id, figi=figi)
    total = 0.0
    stat_df = pd.DataFrame(columns=["date", "time", "sum", "operation"])

    for i in df.index:

        if i > 0 and (df['ema_7'][i - 1] > df['ema_21'][i - 1]) and (df['ema_7'][i] < df['ema_21'][i]) or (
                i > 0 and (isnan(df['ema_21'][i - 1])) and (df['ema_7'][i] < df['ema_21'][i])):
            plt.arrow(x=i, y=df['ema_7'][i] + incr * 120, dx=0, dy=-incr * 80, width=0.6, color='red',
                      head_length=incr * 15)
        elif i > 0 and (df['ema_7'][i - 1] < df['ema_21'][i - 1]) and (df['ema_7'][i] > df['ema_21'][i]) or (
                i > 0 and (isnan(df['ema_21'][i - 1])) and (df['ema_7'][i] > df['ema_21'][i])):
            plt.arrow(x=i, y=df['ema_7'][i] - incr * 120, dx=0, dy=incr * 80, width=0.6, color='green',
                      head_length=incr * 15)

        if i > 0:
            if 1.12 > df["macd"][i - 1] / df["macd"][i] < 0.88:
                if macd_count < 3:
                    macd_count += 1
            elif macd_count > 0:
                macd_count -= 1

        if stop:
            stop = False

        elif not buy_flag:  # Если не было покупки
            if df["macd"][i] > macd_border:
                if df["macd"][i - 1] < df["macd"][i]:  # Если MACD растёт
                    if macd_count < 3:  # Если MACD не стоит на месте
                        if df["adx"][i] > adx_border:
                            if df["ema_7"][i] > df["ema_21"][i]:
                                buy_flag = True
                                plt.axvline(x=i, color="green")
                                buy_price = df["close"][i]
                                insert_df = pd.DataFrame({
                                    "date": [df["time_graph"][i]],
                                    "time": [df["hour_graph"][i]],
                                    "sum": [-(df["low"][i] + df["high"][i]) / 2],
                                    "operation": ["Покупка"],
                                }
                                )
                                stat_df = pd.concat([stat_df, insert_df], ignore_index=True)
                                total -= (df["low"][i] + df["high"][i]) / 2 * 1.003


        elif buy_flag:  # Если была покупка
            if df["ema_7"][i] < df["ema_21"][i] or macd_count >= 4 or (
                    df["macd"][i] / df["macd"][i - 1] < 0.955) or (buy_price / df["close"][i] < 1 - stop_loss) or (
                    buy_price / df["close"][i] > 1 + take_profit):
                buy_flag = False
                plt.axvline(x=i, color="red")
                stop = True
                insert_df = pd.DataFrame({
                    "date": [df["time_graph"][i]],
                    "time": [df["hour_graph"][i]],
                    "sum": [(df["low"][i] + df["high"][i]) / 2],
                    "operation": ["Продажа"],
                }

                )
                stat_df = pd.concat([stat_df, insert_df], ignore_index=True)
                total += (df["low"][i] + df["high"][i]) / 2 * 0.997

    insert_df = pd.DataFrame({
        "date": [0],
        "time": [0],
        "sum": [total],
        "operation": ["Итог"],
    }

    )
    stat_df = pd.concat([stat_df, insert_df], ignore_index=True)

    if hour_graph:
        plt.savefig(f"img/str1/test/graph/hour_{figi}.png")
    else:
        plt.savefig(f"img/str1/test/graph/15_min_{figi}.png")

    plt.clf()

    style_df = df[-11:-1].drop(['time', 'open', 'low', 'high', 'orders'], axis=1)
    style_df = style_df.style.apply(color_macd)

    if hour_graph:
        dfi.export(style_df, f"img/str1/test/ind/hour_{figi}.png")
        dfi.export(stat_df, f"img/str1/test/total/hour_{figi}.png")
    else:
        dfi.export(style_df, f"img/str1/test/ind/15_min_{figi}.png")
        #dfi.export(stat_df, f"img/str1/test/total/15_min_{figi}.png")

    return stat_df
