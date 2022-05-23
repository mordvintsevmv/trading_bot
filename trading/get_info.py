from tinkoff.invest import Client, Quotation, CandleInterval
from config import personal_data
from trading.trade_help import total_quantity
from datetime import datetime, timedelta
import pandas as pd


'''

    Тут представлены все функции, которые позволяют получить какую-либо информацию о счёте
    
    Все данные будут храниться в pandas DataFrame для дальнейшей обработки
    
    Все значения, где количество или суммы представлены с помощью units (целая часть) и nano (дробная часть),
        сразу переводятся в дробные числа для удобства с помощью функции total_quantity.
    
'''


'''
    Функция для получения информации о свободной валюте на счёте
'''


def get_all_currency():
    with Client(personal_data.TOKEN) as client:

        pos = client.operations.get_positions(account_id=personal_data.ACCOUNT_ID_BR)

        cur_df = pd.DataFrame(
            {
                "currency": i.currency,
                "sum": total_quantity(Quotation(units = i.units, nano = i.nano)),
                "units": i.units,
                "nano": i.nano,
            } for i in pos.money
        )

    return cur_df


'''
    Функция для получения информации о всех купленных бумагах
'''


def get_all_shares():
    with Client(personal_data.TOKEN) as client:

        portf = client.operations.get_portfolio(account_id=personal_data.ACCOUNT_ID_BR)

        sh_df = pd.DataFrame(
            {
                "figi": i.figi,
                "instrument": i.instrument_type,
                "quantity": total_quantity(i.quantity),
                "average_price": total_quantity(i.average_position_price),
                "exp_yield": total_quantity(i.expected_yield),
                "nkd": total_quantity(i.current_nkd),
                "average_price_pt": total_quantity(i.average_position_price_pt),
                "current_price": total_quantity(i.current_price),
                "average_price_fifo": total_quantity(i.average_position_price_fifo),
                "lots": total_quantity(i.quantity_lots)
            } for i in portf.positions
        )


    return sh_df



'''
    Функция для получения статистики по счёту
    
    Суммы по всем активам и предполагаемый доход/убыток
'''


def get_all_stat():
    with Client(personal_data.TOKEN) as client:

        portf = client.operations.get_portfolio(account_id=personal_data.ACCOUNT_ID_BR)

        stat_df = pd.DataFrame(
            {
                "sum_shares": total_quantity(portf.total_amount_shares),
                "sum_bonds": total_quantity(portf.total_amount_bonds),
                "sum_etf": total_quantity(portf.total_amount_etf),
                "sum_curr": total_quantity(portf.total_amount_currencies),
                "sum_fut": total_quantity(portf.total_amount_futures),
                "sum_total": total_quantity(portf.total_amount_shares) + total_quantity(portf.total_amount_bonds) + total_quantity(portf.total_amount_etf) + total_quantity(portf.total_amount_currencies) + total_quantity(portf.total_amount_futures),
                "exp_yield": total_quantity(portf.expected_yield),

            }, index=[0]
        )

    return stat_df


'''
    Функция для получения информации о количесвте доступных лотов по figi
    
    Данная функция используется для проверки в боте, можно ли продать указанное количество акций
'''


def get_lots(figi):
    with Client(personal_data.TOKEN) as client:

        portf = client.operations.get_portfolio(account_id=personal_data.ACCOUNT_ID_BR)

        for i in portf.positions:
            if i.figi == figi:
                lots = int(total_quantity(i.quantity_lots))

    return int(lots)



'''
    Функция для получения информации о цене бумаги в портфеле
'''


def get_price(figi):
    with Client(personal_data.TOKEN) as client:

        portf = client.operations.get_portfolio(account_id=personal_data.ACCOUNT_ID_BR)

        for i in portf.positions:
            if i.figi == figi:
                price = total_quantity(i.current_price)

    return price




'''
    Функция для получения списка открытых ордеров
'''


def get_my_order():
    with Client(personal_data.TOKEN) as client:

        ord = client.orders.get_orders(account_id=personal_data.ACCOUNT_ID_BR).orders

        ord_df = pd.DataFrame(
            {
                "order_id": i.order_id,
                "lots_req": i.lots_requested,
                "lots_ex": i.lots_executed,
                "sum_req": total_quantity(i.initial_order_price),
                "sum_ex": total_quantity(i.executed_order_price),
                "sum_total": total_quantity(i.total_order_amount),# сумма после всех комиссий
                "commission": total_quantity(i.initial_commission),
                "serv_commission": total_quantity(i.service_commission),
                "currency": i.currency,
                "figi": i.figi,
                "direction": i.direction,
                "price_one": total_quantity(i.initial_security_price),
                "order_date": i.order_date,
            } for i in ord
        )

    return ord_df


'''
    Функция для получения средней цены акции по свече
    
    В API Tinkoff нет функции, которая позволит узнать стоимость бумаги по FIGI
    По этой причине было решено получить свечки за неделю и взять последнюю доступную.
    Такое решение связано с тем, что торги не проходят в выходные дни, поэтому наилучшим решением будет выбрать
        большой интервал времени для избежания ошибок.  
'''


def get_price_figi(figi):

    with Client(personal_data.TOKEN) as client:

        r = client.market_data.get_candles(
            figi=figi,
            from_=datetime.utcnow() - timedelta(days=7),
            to=datetime.utcnow(),
            interval=CandleInterval.CANDLE_INTERVAL_HOUR
        )

    # Выбираем последнюю доступную свечку
    # Получаем среднюю стоимость бумаги путём складывания самой высокой и самой низкой цен
    average_price = ((total_quantity(r.candles[-1].high) + total_quantity(r.candles[-1].low))/2)

    return average_price



