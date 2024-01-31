import os


telegram_token = '6690193206:AAFZGXOfXbkOK4tS-zAE6FCzNJ8R9S2LgE0'
payment_token = '6916772465:AAFIVmoM1fMFmNBspZpwmQbzUNHXhA9USOQ'
path_to_browser = "/usr/bin/google-chrome"
limit_queue = 3
days_delay_weekly = 7
days_delay_daily = 1


private_group_id = -1001943751912
standard_group_id = -1001919068990
premium_chat_group_id = -1002040787460

data_base = os.path.join(os.path.dirname(__file__), 'database.db')

ethscan_api_key = "PDZMXAR2GWRXYWUIS14NSQ9WS4EPTIKIFI"
infura_url = 'https://mainnet.infura.io/v3/8b6f204cc9d14fc0a0f48fb531a46384'
owner_wallet = "0xB604E5e0A444068b2c00B2D730350E76c058df4f"
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