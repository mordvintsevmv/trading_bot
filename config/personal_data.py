import os
from dotenv import load_dotenv

"""
    Все персональные данные хранятся в файле .env для обеспечения безопасности 
"""
load_dotenv()
TOKEN = os.environ.get("TOKEN")
ACCOUNT_ID_BR = os.environ.get("ACCOUNT_ID_BR")

BOT_TOKEN = os.environ.get("BOT_TOKEN")
#ADMIN_ID = os.environ.get("ADMIN_ID")
