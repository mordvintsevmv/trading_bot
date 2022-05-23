from tinkoff.invest import Client
from config import personal_data
from trading.trade_help import total_quantity

"""

    Тут собраны все функции, которые позволяют получить FIGI по тикеру бумаги
    или тикер бумаги по FIGI
    
    Тинькофф использует для всех операций покупок/продаж FIGI, 
    при этом для человеческого восприятия удобнее использовать название компании.
    
    Например. Акции ВТБ:
    FIGI = "BBG004730ZJ9"
    Ticker = "VTBR"
    Name = "Банк ВТБ"

"""


'''
    Функция для получения ценной бумаги по FIGI
'''

def sfb_by_figi(figi):
    with Client(personal_data.TOKEN) as client:

        try:
            sfb = client.instruments.get_instrument_by(id_type=1,id=figi).instrument
            return sfb
        except Exception as ex:
            print(ex)

        return 0


'''
    Функция для получения названия бумаги по FIGI
'''


def sfb_name_by_figi(figi):
    with Client(personal_data.TOKEN) as client:

        try:
            sfb_name = client.instruments.get_instrument_by(id_type=1, id=figi).instrument.name
            return sfb_name
        except Exception as ex:
            print(ex)

    return 0


'''
    Функция для получения минимального шага цены по FIGI
'''


def sfb_incr_by_figi(figi):
    with Client(personal_data.TOKEN) as client:

        try:
            sfb_incr = total_quantity(client.instruments.get_instrument_by(id_type=1, id=figi).instrument.min_price_increment)
            return sfb_incr
        except Exception as ex:
            print(ex)

    return 0
