import os
import sqlite3 as sl
from dotenv import load_dotenv


"""
    Все персональные данные хранятся в файле .env для обеспечения безопасности 
"""


load_dotenv()

def get_token(user_id):
    conn = sl.connect("db/users.db")
    cur = conn.cursor()

    token = cur.execute('SELECT token FROM USER WHERE id = ? ', (user_id,)).fetchone()[0]
    return token


def get_account(user_id):
    conn = sl.connect("db/users.db")
    cur = conn.cursor()

    account_id = cur.execute('SELECT account_id FROM USER WHERE id = ? ', (user_id,)).fetchone()[0]
    return account_id

def get_account_type(user_id):
    conn = sl.connect("db/users.db")
    cur = conn.cursor()

    account_type = cur.execute('SELECT account_type FROM USER WHERE id = ? ', (user_id,)).fetchone()[0]
    return account_type

BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = os.environ.get("ADMIN_ID")
