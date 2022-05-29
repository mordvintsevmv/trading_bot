import sqlite3 as sl


def create_tables():
    conn_op = sl.connect("db/operations.db")

    conn_op.execute('CREATE TABLE IF NOT EXISTS OPERATIONS ('
                    'id INTEGER PRIMARY KEY NOT NULL,'
                    'user_id TEXT,'
                    'account_id TEXT,'
                    'account_type TEXT,'
                    'order_id TEXT,'
                    'date_op TEXT,'
                    'time_op TEXT,'
                    'operation TEXT,'
                    'figi TEXT,'
                    'name TEXT,'
                    'quantity_lots INTEGER,'
                    'quantity_total INTEGER,'
                    'price REAL,'
                    'price_total REAL,'
                    'commission REAL,'
                    'via TEXT)')

    conn_str1 = sl.connect("db/str1.db")

    conn_str1.execute('CREATE TABLE IF NOT EXISTS CONFIG ('
                      'id INTEGER PRIMARY KEY NOT NULL,'
                      'user_id TEXT,'
                      'account_id TEXT,'
                      'figi TEXT,'
                      'name TEXT,'
                      'trade_status TEXT,'
                      'notif_status TEXT,'
                      'buy_price REAL,'
                      'period INTEGER,'
                      'macd_border REAL,'
                      'adx_border REAL,'
                      'take_profit REAL,'
                      'stop_loss REAL)')

    conn_user = sl.connect("db/users.db")

    conn_user.execute('CREATE TABLE IF NOT EXISTS USER ('
                      'id INTEGER PRIMARY KEY NOT NULL,'
                      'first_name TEXT,'
                      'last_name TEXT,'
                      'username TEXT,'
                      'token TEXT,'
                      'account_id TEXT,'
                      'account_type TEXT)')
