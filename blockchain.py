import asyncio
import requests
import random
from web3 import Web3, HTTPProvider
from config import *


async def get_usd_value_from_eth(eth):
    with open("Webshare 100 proxies.txt", 'r') as file:
        proxy_list = file.read().split("\n")
        proxy = proxy_list[random.randrange(0, len(proxy_list))].split(":")
        proxy_address, proxy_port, proxy_username, proxy_password = proxy[0], proxy[1], proxy[2], proxy[3]
        proxies = {
            'http': f'http://{proxy_username}:{proxy_password}@{proxy_address}:{proxy_port}',
        }

    url = "https://api.coingecko.com/api/v3/coins/ethereum"
    coingecko_response = requests.get(url, proxies=proxies)
    if coingecko_response.status_code == 200:
        result = coingecko_response.json()
        eth_usd_price = result['market_data']['current_price']['usd']
        return round(eth_usd_price * eth, 4)


async def compare_amounts(expected_amount, actual_amount, deviation_percent):
    deviation = expected_amount * (deviation_percent / 100)
    lower_limit = expected_amount - deviation
    upper_limit = expected_amount + deviation

    return lower_limit <= actual_amount <= upper_limit


async def check_transaction_hash(tx_hash):
    # internal
    txs_url_internal = f"https://api.etherscan.io/api?module=account&action=txlistinternal&address={owner_wallet}&startblock=0&endblock=999999999&page=1&offset=10000&sort=asc&apikey={ethscan_api_key}"
    response_txs_internal = requests.get(txs_url_internal)
    if response_txs_internal.status_code == 200:
        result_list_internal = response_txs_internal.json()['result']
        for tx in result_list_internal:
            if tx_hash == tx['hash']:
                tx_hash_current = tx["hash"]
                eth_value = float(tx["value"]) / 10 ** 18
                print(tx_hash_current, eth_value, "ETH", True)
                usd_value_of_eth = await get_usd_value_from_eth(eth_value)
                actual_amount = float(usd_value_of_eth)
                for package, expected_amount in price_packages_usdt_usdc.items():
                    tx_verdict = await compare_amounts(expected_amount, actual_amount, deviation_percent)
                    if tx_verdict == True:
                        paid_package = package
                        return True, paid_package

    # usdt / usdc erc-20
    txs_url_erc20 = f"https://api.etherscan.io/api?module=account&action=tokentx&address={owner_wallet}&page=1&offset=10000&startblock=0&endblock=999999999&sort=asc&apikey={ethscan_api_key}"
    response_txs_erc20 = requests.get(txs_url_erc20)
    if response_txs_erc20.status_code == 200:
        result_list_erc20 = response_txs_erc20.json()['result']
        for tx in result_list_erc20:
            if tx_hash == tx["hash"]:
                if tx["to"].lower() == owner_wallet.lower():
                    tx_hash_current = tx["hash"]
                    contract_address = tx["contractAddress"]
                    value = int(tx["value"]) / 10 ** int(tx["tokenDecimal"])
                    if int(value) == 0:
                        value = round(int(tx["value"]) / 10 ** int(tx["tokenDecimal"]), 5)
                    else:
                        value = int(value)
                    coin = tx["tokenSymbol"]
                    if "https://" in coin:
                        lt = coin.split(" ")
                        for elem in lt:
                            if "https://" in elem:
                                coin = elem.replace("https://", "")
                                break
                    timestamp = tx["timeStamp"]

                    if coin == "USDT":
                        print(tx_hash_current, value, "USDT", True)
                        actual_amount = float(value)
                        for package, expected_amount in price_packages_usdt_usdc.items():
                            tx_verdict = await compare_amounts(expected_amount, actual_amount, deviation_percent)
                            if tx_verdict == True:
                                paid_package = package
                                return True, paid_package

                    elif coin == "USDC":
                        print(tx_hash_current, value, "USDC", True)
                        actual_amount = float(value)
                        for package, expected_amount in price_packages_usdt_usdc.items():
                            tx_verdict = await compare_amounts(expected_amount, actual_amount, deviation_percent)
                            if tx_verdict == True:
                                paid_package = package
                                return True, paid_package


    # ethereum native
    txs_url_native = f"https://api.etherscan.io/api?module=account&action=txlist&address={owner_wallet}&startblock=0&endblock=99999999&page=1&offset=10000&sort=asc&apikey={ethscan_api_key}"
    response_txs_native = requests.get(txs_url_native)
    if response_txs_native.status_code == 200:
        result_list_native = response_txs_native.json()['result']
        for tx in result_list_native:
            if tx_hash == tx["hash"]:
                if tx["to"].lower() == owner_wallet.lower():
                    if tx['input'] == '0x':
                        tx_hash_current = tx["hash"]
                        value = float(tx["value"]) / 10**18
                        print(tx_hash_current, value, "ETH", True)
                        usd_value_of_eth = await get_usd_value_from_eth(value)
                        actual_amount = float(usd_value_of_eth)
                        for package, expected_amount in price_packages_usdt_usdc.items():
                            tx_verdict = await compare_amounts(expected_amount, actual_amount, deviation_percent)
                            if tx_verdict == True:
                                paid_package = package
                                return True, paid_package
    return False, 0


async def get_eth_value_from_usd(usd):
    with open("Webshare 100 proxies.txt", 'r') as file:
        proxy_list = file.read().split("\n")
        proxy = proxy_list[random.randrange(0, len(proxy_list))].split(":")
        proxy_address, proxy_port, proxy_username, proxy_password = proxy[0], proxy[1], proxy[2], proxy[3]
        proxies = {
            'http': f'http://{proxy_username}:{proxy_password}@{proxy_address}:{proxy_port}',
        }

    url = "https://api.coingecko.com/api/v3/coins/ethereum"
    coingecko_response = requests.get(url, proxies=proxies)
    if coingecko_response.status_code == 200:
        result = coingecko_response.json()
        eth_usd_price = result['market_data']['current_price']['usd']
        return round(usd / eth_usd_price, 4)


async def get_eth_price():
    with open("Webshare 100 proxies.txt", 'r') as file:
        proxy_list = file.read().split("\n")
        proxy = proxy_list[random.randrange(0, len(proxy_list))].split(":")
        proxy_address, proxy_port, proxy_username, proxy_password = proxy[0], proxy[1], proxy[2], proxy[3]
        proxies = {
            'http': f'http://{proxy_username}:{proxy_password}@{proxy_address}:{proxy_port}',
        }

    url = "https://api.coingecko.com/api/v3/coins/ethereum"
    coingecko_response = requests.get(url, proxies=proxies)
    if coingecko_response.status_code == 200:
        result = coingecko_response.json()
        return result['market_data']['current_price']['usd']


