from tinkoff.invest import Client, OrderDirection, OrderType
from trading import trade_help
from config import personal_data
from datetime import datetime
from trading.trade_help import total_quantity

"""

    Тут представлены все функции, которые отвечает за размещение ордеров на покупку/продаужу бумаг

"""

'''
    Функция для покупки ценных бумаг по заданной цене за бумагу
    Если цена не задана (равна нулю), то бумаги покупаются по лучшей рыночной цене
'''


async def buy_sfb(figi, price, quantity_lots):
    with Client(personal_data.TOKEN) as client:

        if price > 0.0:
            r = client.orders.post_order(
                order_id=str(datetime.utcnow().timestamp()),
                figi=figi,
                price=trade_help.to_quotation(price),
                quantity=quantity_lots,
                account_id=personal_data.ACCOUNT_ID_BR,
                direction=OrderDirection.ORDER_DIRECTION_BUY,
                order_type=OrderType.ORDER_TYPE_LIMIT,
            )
        else:
            r = client.orders.post_order(
                order_id=str(datetime.utcnow().timestamp()),
                figi=figi,
                quantity=quantity_lots,
                account_id=personal_data.ACCOUNT_ID_BR,
                direction=OrderDirection.ORDER_DIRECTION_BUY,
                order_type=OrderType.ORDER_TYPE_MARKET,
            )
    return total_quantity(r.executed_order_price)


'''
    Функция для продажи ценных бумаг по заданной цене за бумагу
    Если цена не задана (равна нулю), то бумаги продаются по лучшей рыночной цене
'''


async def sell_sfb(figi, price, quantity_lots):
    with Client(personal_data.TOKEN) as client:

        if price > 0.0:
            r = client.orders.post_order(
                order_id=str(datetime.utcnow().timestamp()),
                figi=figi,
                quantity=quantity_lots,
                price = trade_help.to_quotation(price),
                account_id=personal_data.ACCOUNT_ID_BR,
                direction=OrderDirection.ORDER_DIRECTION_SELL,
                order_type=OrderType.ORDER_TYPE_LIMIT,
            )
        else:
            r = client.orders.post_order(
                order_id=str(datetime.utcnow().timestamp()),
                figi=figi,
                quantity=quantity_lots,
                account_id=personal_data.ACCOUNT_ID_BR,
                direction=OrderDirection.ORDER_DIRECTION_SELL,
                order_type=OrderType.ORDER_TYPE_MARKET,
            )
    return total_quantity(r.executed_order_price)

'''
    Функция для отмены ордера по его id
'''


async def cancel_order(order_id):
    with Client(personal_data.TOKEN) as client:

        r = client.orders.cancel_order(
            order_id=order_id,
            account_id=personal_data.ACCOUNT_ID_BR,
            )
    return r



