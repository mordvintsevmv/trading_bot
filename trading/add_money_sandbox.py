from tinkoff.invest import Client, Quotation, CandleInterval
from trading.trade_help import total_quantity, to_quotation
from datetime import datetime, timedelta
import pandas as pd
from config.personal_data import get_token, get_account, get_account_type
from tinkoff.invest import MoneyValue


def add_money_sandbox(user_id, sum, cur):
    with Client(get_token(user_id)) as client:

        units = to_quotation(float(sum)).units
        nano = to_quotation(float(sum)).nano

        client.sandbox.sandbox_pay_in(
            account_id=get_account(user_id),
            amount=MoneyValue(units=units, nano=nano, currency=f"{cur}")
        )

    return 0
