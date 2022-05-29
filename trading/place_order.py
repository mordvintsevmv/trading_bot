from tinkoff.invest import Client, OrderDirection, OrderType
from trading import trade_help
from config.personal_data import get_token, get_account, get_account_type
from datetime import datetime
from trading.trade_help import total_quantity
import sqlite3 as sl
from datetime import datetime
from trading.get_by_figi import sfb_name_by_figi
from trading.trade_help import share_lot_figi

"""

    Тут представлены все функции, которые отвечает за размещение ордеров на покупку/продаужу бумаг

"""

'''
    Функция для покупки ценных бумаг по заданной цене за бумагу
    Если цена не задана (равна нулю), то бумаги покупаются по лучшей рыночной цене
'''


def buy_sfb(figi, price, quantity_lots, user_id, via="else"):
    with Client(get_token(user_id)) as client:

        if get_account_type(user_id) == "sandbox":
            if price > 0.0:
                r = client.sandbox.post_sandbox_order(
                    order_id=str(datetime.utcnow().timestamp()),
                    figi=figi,
                    price=trade_help.to_quotation(price),
                    quantity=quantity_lots,
                    account_id=get_account(user_id),
                    direction=OrderDirection.ORDER_DIRECTION_BUY,
                    order_type=OrderType.ORDER_TYPE_LIMIT,
                )
            else:
                r = client.sandbox.post_sandbox_order(
                    order_id=str(datetime.utcnow().timestamp()),
                    figi=figi,
                    quantity=quantity_lots,
                    account_id=get_account(user_id),
                    direction=OrderDirection.ORDER_DIRECTION_BUY,
                    order_type=OrderType.ORDER_TYPE_MARKET,
                )
        else:
            if price > 0.0:
                r = client.orders.post_order(
                    order_id=str(datetime.utcnow().timestamp()),
                    figi=figi,
                    price=trade_help.to_quotation(price),
                    quantity=quantity_lots,
                    account_id=get_account(user_id),
                    direction=OrderDirection.ORDER_DIRECTION_BUY,
                    order_type=OrderType.ORDER_TYPE_LIMIT,
                )
            else:
                r = client.orders.post_order(
                    order_id=str(datetime.utcnow().timestamp()),
                    figi=figi,
                    quantity=quantity_lots,
                    account_id=get_account(user_id),
                    direction=OrderDirection.ORDER_DIRECTION_BUY,
                    order_type=OrderType.ORDER_TYPE_MARKET,
                )
    commission = total_quantity(r.initial_commission)
    write_operation(figi=figi, price=price, commission=commission, quantity_lots=quantity_lots, user_id=user_id,
                    order_id=r.order_id, operation="buy", via=via)

    return total_quantity(r.executed_order_price)


'''
    Функция для продажи ценных бумаг по заданной цене за бумагу
    Если цена не задана (равна нулю), то бумаги продаются по лучшей рыночной цене
'''


def sell_sfb(figi, price, quantity_lots, user_id, via="else"):
    with Client(get_token(user_id)) as client:

        if get_account_type(user_id) == "sandbox":
            if price > 0.0:
                r = client.sandbox.post_sandbox_order(
                    order_id=str(datetime.utcnow().timestamp()),
                    figi=figi,
                    quantity=quantity_lots,
                    price=trade_help.to_quotation(price),
                    account_id=get_account(user_id),
                    direction=OrderDirection.ORDER_DIRECTION_SELL,
                    order_type=OrderType.ORDER_TYPE_LIMIT,
                )
            else:
                r = client.sandbox.post_sandbox_order(
                    order_id=str(datetime.utcnow().timestamp()),
                    figi=figi,
                    quantity=quantity_lots,
                    account_id=get_account(user_id),
                    direction=OrderDirection.ORDER_DIRECTION_SELL,
                    order_type=OrderType.ORDER_TYPE_MARKET,
                )
        else:
            if price > 0.0:
                r = client.orders.post_order(
                    order_id=str(datetime.utcnow().timestamp()),
                    figi=figi,
                    quantity=quantity_lots,
                    price=trade_help.to_quotation(price),
                    account_id=get_account(user_id),
                    direction=OrderDirection.ORDER_DIRECTION_SELL,
                    order_type=OrderType.ORDER_TYPE_LIMIT,
                )
            else:
                r = client.orders.post_order(
                    order_id=str(datetime.utcnow().timestamp()),
                    figi=figi,
                    quantity=quantity_lots,
                    account_id=get_account(user_id),
                    direction=OrderDirection.ORDER_DIRECTION_SELL,
                    order_type=OrderType.ORDER_TYPE_MARKET,
                )
    commission = total_quantity(r.initial_commission)
    write_operation(figi=figi, price=price, commission=commission, quantity_lots=quantity_lots, user_id=user_id,
                    order_id=r.order_id, operation="sell", via=via)
    return total_quantity(r.executed_order_price)


'''
    Функция для отмены ордера по его id
'''


async def cancel_order(order_id, user_id, via="else"):
    with Client(get_token(user_id)) as client:

        if get_account_type(user_id) == "sandbox":
            state = client.sandbox.get_sandbox_order_state(
                order_id=order_id,
                account_id=get_account(user_id),
            )

            r = client.sandbox.cancel_sandbox_order(
                order_id=order_id,
                account_id=get_account(user_id),
            )
        else:
            state = client.orders.get_order_state(
                order_id=order_id,
                account_id=get_account(user_id),
            )

            r = client.orders.cancel_order(
                order_id=order_id,
                account_id=get_account(user_id),
            )

    conn = sl.connect("db/operations.db")
    cur = conn.cursor()

    info = cur.execute('SELECT * FROM OPERATIONS WHERE order_id=?', (order_id,))
    if info.fetchone() is not None:
        quantity_lots = state.lots_executed
        price = total_quantity(state.executed_order_price)
        commission = total_quantity(state.executed_commission)
        operation = cur.execute('SELECT operation FROM OPERATIONS WHERE order_id = ?;', (order_id,)).fetchone()[
                        0] + "/canceled"
        quantity_total = quantity_lots * share_lot_figi(state.figi, user_id=user_id)
        price_total = quantity_total * price

        new_operation = (quantity_lots, quantity_total, price_total, commission, operation, order_id)

        cur.execute(
            'UPDATE OPERATIONS SET quantity_lots = ?, quantity_total = ?, price_total = ?, commission = ?, operation '
            '= ? WHERE order_id '
            '= ?;',
            new_operation)
        conn.commit()

    return r


def write_operation(figi, price, commission, quantity_lots, user_id, order_id, operation, via="else"):
    conn = sl.connect("db/operations.db")
    cur = conn.cursor()

    date_op = datetime.now().strftime("%d.%m.%Y")
    time_op = datetime.now().strftime("%H:%M:%S")
    name = sfb_name_by_figi(figi, user_id)
    account_type = get_account_type(user_id)
    account_id = get_account(user_id)
    quantity_total = quantity_lots * share_lot_figi(figi=figi, user_id=user_id)
    price_total = quantity_total * price

    operation = (
        user_id, account_id, account_type, order_id, date_op, time_op, operation, figi, name, quantity_lots,
        quantity_total, price, price_total,
        commission, via)
    cur.execute("INSERT INTO OPERATIONS (user_id, account_id, account_type, order_id, date_op, time_op, operation, "
                "figi, name, "
                "quantity_lots, quantity_total, price, price_total, commission, via) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);",
                operation)
    conn.commit()
