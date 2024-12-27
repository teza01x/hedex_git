import os


telegram_token = ''
payment_token = ''
path_to_browser = "/usr/bin/google-chrome"
limit_queue = 3
days_delay_weekly = 7
days_delay_daily = 1


private_group_id = -11111
standard_group_id = -11111
premium_chat_group_id = -11111

data_base = os.path.join(os.path.dirname(__file__), 'database.db')

ethscan_api_key = ""
infura_url = 'https://mainnet.infura.io/v3/
owner_wallet = ""
deviation_percent = 5

price_packages_usdt_usdc = {
    1 : 100, # premium
    2 : 300,
    3 : 1000,
    4 : 175, # bronze
    5 : 525,
    6 : 1600,
    7 : 225, # silver
    8 : 675,
    9 : 2000,
    10 : 275, # gold
    11 : 825,
    12 : 2400,
}
