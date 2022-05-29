from tinkoff.invest import Quotation, Client
from config.personal_data import get_account, get_token, get_account_type
import math
from datetime import datetime, timedelta
import pytz


"""

    Тут представлены все небольшие вспомогательные функции

"""

'''
    Функция для расчёта полной стоимости актива / общего количества средств
    Тинькофф возвращает стоимость в units и nano
    units - целая часть
    nano - дробная (9 знаков после запятой)
'''


def total_quantity(quantity):
    total_quantity = quantity.units + (quantity.nano * (1e-9))
    return total_quantity


'''
    Функция для перевода дробного числа в Quotation
    Тинькофф получает стоимость в units и nano
    units - целая часть
    nano - дробная (9 знаков после запятой)
'''


def to_quotation(price):
    quo = Quotation()
    quo.units = int(math.modf(price)[1])
    quo.nano = int(round(math.modf(price)[0] * (1e9)))
    return quo


'''
    Позволяет узнать количесвто АКЦИЙ в одном лоте по FIGI
'''


def share_lot_figi(figi, user_id):
    with Client(get_token(user_id)) as client:

        sh = client.instruments.shares()
        for i in sh.instruments:
            if i.figi == figi: in_lot = i.lot
    return int(in_lot)


'''
    Позволяет узнать, есть ли такая АКЦИЯ в портфеле
    Сравнение идёт по FIGI
'''


def in_portf(figi, user_id):
    with Client(get_token(user_id)) as client:

        if get_account_type(user_id=user_id) == "sandbox":
            portf = client.sandbox.get_sandbox_portfolio(account_id=get_account(user_id))
        else:
            portf = client.operations.get_portfolio(account_id=get_account(user_id))
        for i in portf.positions:
            if i.figi == figi:
                return True
    return False


'''
    Позволяет узнать, существует ли такая бумага в прицнипе
'''


def in_shares(figi, user_id):
    with Client(get_token(user_id)) as client:
        try:
            sh = client.instruments.get_instrument_by(id_type=1,id=figi)
        except:
            return False

        return True



'''
    Позволяет узнать, идут ли сейчас торги
'''


def is_trade(figi, user_id):

    # Получаем расписание всех площадок за неделю
    with Client(get_token(user_id)) as client:
        sch = client.instruments.trading_schedules(
            from_=datetime.utcnow(),
            to=datetime.utcnow() + timedelta(days=6),
        ).exchanges

        # Получаем инструмент
        try:
            sfb = client.instruments.get_instrument_by(id_type=1, id=figi).instrument
        except Exception as ex:
            print(ex)
            return False

        # Получаем время сейчас в часовом поясе UTC
        now = datetime.utcnow().replace(tzinfo=pytz.UTC)

        for i in sch:
            if i.exchange == sfb.exchange: # Если совпадают торговые площадки
                for j in i.days:
                    if j.is_trading_day and j.start_time < now < j.end_time:
                        return True
                    elif j.is_trading_day:
                        print(
                            f"Бумаги {sfb.name}\n"
                            f"FIGI: {sfb.figi}\n"
                            f"Площадка: {sfb.exchange}\n"
                            f"До торгов осталось: {j.start_time-now}"
                        )
                        return False

    return False
