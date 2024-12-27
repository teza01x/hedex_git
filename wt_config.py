import os
import time


telegram_wt_token = ''

wt_database = os.path.join(os.path.dirname(__file__), 'wt_database.db')
wallet_txs_database = os.path.join(os.path.dirname(__file__), 'wallet_txs_database.db')
etherscan_database = os.path.join(os.path.dirname(__file__), 'etherscan_keys.db')
proxy_file = os.path.join(os.path.dirname(__file__), 'Webshare 100 proxies.txt')

BASIC_MENU_STATUS = 0
ENTER_WALLET_ADDRESS_STATUS = 1
ENTER_WALLET_NAME_STATUS = 2
RENAME_WALLET_NAME_STATUS = 3


limitations = {
    10: ("Free Tier (10 wallets)", "Noti Customisation: ❌\nHedex Premium Channel: ❌\nHedex Personal: ❌"),
    30: ("Bronze Tier (30 wallets)", "Noti Customisation: ✅\nHedex Premium Channel: ✅\nHedex Personal: ❌"),
    75: ("Silver Tier (75 wallets)", "Noti Customisation: ✅\nHedex Premium Channel: ✅\nHedex Personal: ✅"),
    150: ("Gold Tier (150 wallets)", "Noti Customisation: ✅\nHedex Premium Channel: ✅\nHedex Personal: ✅"),
}


api_keys = []
