import asyncio
import aiohttp
import time
import random
from async_sql_scripts_wt import *
from wt_config import *


async def find_all_txs_to_wallet(wallet_address, api_key, proxy_url, db_queue):
    try:
        txs_url = f"https://api.etherscan.io/api?module=account&action=tokentx&address={wallet_address}&page=1&offset=10000&startblock=0&endblock=999999999&sort=asc&apikey={api_key}"
        async with aiohttp.ClientSession() as session:
            async with session.get(txs_url, proxy=proxy_url) as response_txs:
                try:
                    if response_txs.status == 200:
                        result_list = await response_txs.json()
                        try:
                            txs_list = result_list['result']

                            current_time = int(time.time())
                            two_hours_ago = current_time - (2 * 60 * 60)

                            txs_count = 0
                            for tx in txs_list[::-1]:
                                if tx["to"].lower() == wallet_address.lower():
                                    tx_hash = tx["hash"]
                                    contract_address = tx["contractAddress"]
                                    try:
                                        value = int(tx["value"]) / 10 ** int(tx["tokenDecimal"])
                                    except:
                                        value = int(tx["value"])
                                    if int(value) == 0:
                                        value = str(round(int(tx["value"]) / 10 ** int(tx["tokenDecimal"]), 5))
                                    else:
                                        value = str(int(value))
                                    coin = tx["tokenSymbol"]
                                    if "https://" in coin:
                                        lt = coin.split(" ")
                                        for elem in lt:
                                            if "https://" in elem:
                                                coin = elem.replace("https://", "")
                                                break
                                    timestamp = tx["timeStamp"]
                                    if int(timestamp) >= two_hours_ago:
                                        await insert_new_wallet_txs(wallet_address, tx_hash, contract_address, value, coin, timestamp, api_key, db_queue)

                                    txs_count += 1
                                    if txs_count == 10:
                                        break
                        except Exception as error:
                            print("Error while processing wallet: {}\nERROR: {}".format(wallet_address, error))
                    else:
                        print("Error with status code of response: {}".format(response_txs.status))
                except Exception as error:
                    print("Error while processing wallet: {}\nERROR: {}".format(wallet_address, error))
    except Exception as error:
        print("Error finding wallet txs.\nProxy: {}".format(proxy_url))
        print(error)


async def worker_func(wallets, api_keys, db_queue):
    try:
        api_key_index = 0
        tasks = []
        api_requests = 0
        cycle_requests = 0
        max_requests_per_api_key = 5
        max_requests_per_cycle = (len(api_keys)-1) * max_requests_per_api_key

        proxy_index = 0
        with open(proxy_file, 'r') as file:
            data_file = file.read()
            data = data_file.split("\n")
            data = [i for i in data if len(i) > 0]

        while wallets:
            current_unix_time = time.time()
            past_unix_time = await unix_time_api_key(api_keys[api_key_index])

            if current_unix_time > past_unix_time:
                for _ in range(min(max_requests_per_api_key, len(wallets))):
                    proxy_data = data[proxy_index]
                    proxy_data = proxy_data.split(":")
                    proxy_url = f'http://{proxy_data[2]}:{proxy_data[3]}@{proxy_data[0]}:{proxy_data[1]}'

                    wallet_address = wallets.pop(0)
                    task = asyncio.create_task(find_all_txs_to_wallet(wallet_address, api_keys[api_key_index], proxy_url, db_queue))
                    tasks.append(task)
                    cycle_requests += 1
                    api_requests += 1
                    proxy_index = (proxy_index + 1) % len(data)
                    await asyncio.sleep(0.05)

                    if api_requests >= max_requests_per_api_key:
                        await write_new_unix_time(str(current_unix_time + 1), api_keys[api_key_index])
                        api_key_index = (api_key_index + 1) % len(api_keys)
                        api_requests = 0
                        await asyncio.sleep(0.1)

                    if cycle_requests >= max_requests_per_cycle:
                        cycle_requests = 0
                        await asyncio.sleep(1)
            else:
                api_key_index = (api_key_index + 1) % len(api_keys)
                proxy_index = (proxy_index + 1) % len(data)
                await asyncio.sleep(0.1)
        await asyncio.gather(*tasks)
    except Exception as error:
        print("Error in worker function")
        print(error)


async def gather_wallet_transactions():
    while True:
        try:
            start_time = time.time()

            unique_wallets = list()
            wallets_db = list()
            user_ids = await get_all_user_ids()
            for user_id in user_ids:
                all_users_wallets = await get_user_wallets(user_id)
                wallet_limit = await check_user_sub_tier(user_id)
                if len(all_users_wallets) > wallet_limit:
                    all_users_wallets = all_users_wallets[:wallet_limit]
                unique_wallets += all_users_wallets

            wallets_db = [wallet for wallet in unique_wallets if wallet not in wallets_db]

            # wallets_db = await get_all_tracking_wallets()
            # wallet_lists = [wallets_db[:500]]
            wallet_lists = list()
            max_size = 500
            if len(wallets_db) > max_size:
                for i in range(0, len(wallets_db), max_size):
                    wallet_lists.append(wallets_db[i:i + max_size])
            else:
                wallet_lists = [wallets_db]

            for wallets in wallet_lists:
                db_queue = asyncio.Queue()

                db_queue_processor_task = asyncio.create_task(process_db_queue(db_queue))

                await worker_func(wallets, api_keys, db_queue)

                db_queue_processor_task.cancel()
                try:
                    await db_queue_processor_task
                except asyncio.CancelledError:
                    pass
                await asyncio.sleep(1)


            end_time = time.time()
            elapsed_time = end_time - start_time
            print(f"Execute time: {elapsed_time} секунд")
            await asyncio.sleep(10)
        except Exception as error:
            print("Error in main function")
            print(error)
            await asyncio.sleep(10)


async def main():
    try:
        get_newest_transactions = asyncio.create_task(gather_wallet_transactions())
        await asyncio.gather(get_newest_transactions)
    except Exception as error:
        print(error)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()
