import aiosqlite
import asyncio
import time
import random
from contextlib import asynccontextmanager
from wt_config import *


@asynccontextmanager
async def get_connection():
    conn = await aiosqlite.connect(wallet_txs_database)
    try:
        yield conn
    finally:
        await conn.close()


async def insert_new_wallet_txs(wallet_address, tx_hash, contract_address, value, coin, timestamp, api_key, db_queue):
    query = f'''
        INSERT INTO wallets_transactions (transaction_hash, wallet_address, contract_address, value, coin, timestamp, notified)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(transaction_hash)
        DO UPDATE SET
            contract_address = excluded.contract_address,
            value = excluded.value,
            coin = excluded.coin,
            timestamp = excluded.timestamp;
    '''
    params = (tx_hash, wallet_address, contract_address, value, coin, timestamp, "")

    await db_queue.put({
        "query": query,
        "params": params
    })


async def process_db_queue(db_queue):
    try:
        while True:
            task = await db_queue.get()
            try:
                async with get_connection() as conn:
                    await conn.execute(task["query"], task["params"])
                    await conn.commit()
            except Exception as e:
                print(f"Error in database msg1: {e}")
            finally:
                db_queue.task_done()
    except asyncio.CancelledError:
        while not db_queue.empty():
            task = await db_queue.get()
            try:
                async with get_connection() as conn:
                    await conn.execute(task["query"], task["params"])
                    await conn.commit()
            except Exception as e:
                print(f"Error in database msg2: {e}")
            finally:
                db_queue.task_done()

    except Exception as e:
        print(f"Error in database msg3: {e}")


async def unix_time_api_key(api_key):
    async with aiosqlite.connect(etherscan_database) as conn:
        async with conn.cursor() as cursor:
            unix_time = await cursor.execute("SELECT next_time_use FROM etherscan_keys WHERE key = ?", (api_key,))
            unix_time = await unix_time.fetchone()
            return float(unix_time[0])


async def write_new_unix_time(current_unix_time, api_key):
    async with aiosqlite.connect(etherscan_database) as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("UPDATE etherscan_keys SET next_time_use = ? WHERE key = ?", (current_unix_time, api_key,))
            await conn.commit()


async def get_all_user_ids():
    async with aiosqlite.connect(wt_database) as conn:
        async with conn.cursor() as cursor:
            result = await cursor.execute("SELECT user_id FROM user")
            result = [i[0] for i in await result.fetchall()]
            return result


async def get_users_active_status(user_id):
    async with aiosqlite.connect(wt_database) as conn:
        async with conn.cursor() as cursor:
            result = await cursor.execute("SELECT activity_status FROM user WHERE user_id = ?", (user_id,))
            result = await result.fetchone()
            return result[0]


async def change_users_activity_status(user_id, act_status):
    async with aiosqlite.connect(wt_database) as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("UPDATE user SET activity_status = ? WHERE user_id = ?", (act_status, user_id,))
            await conn.commit()


async def get_all_active_user_ids():
    async with aiosqlite.connect(wt_database) as conn:
        async with conn.cursor() as cursor:
            result = await cursor.execute("SELECT user_id FROM user WHERE activity_status = ?", (1,))
            result = [i[0] for i in await result.fetchall()]
            return result


async def get_user_wallets(user_id):
    async with aiosqlite.connect(wt_database) as conn:
        async with conn.cursor() as cursor:
            result = await cursor.execute("SELECT wallet_address FROM tracking_wallets WHERE user_id = ?",(user_id,))
            result = [i[0] for i in await result.fetchall()]
            return result


async def get_wallets_trigger_count(user_id):
    async with aiosqlite.connect(wt_database) as conn:
        async with conn.cursor() as cursor:
            result = await cursor.execute("SELECT wallets_trigger_count FROM user WHERE user_id = ?",(user_id,))
            result = await result.fetchone()
            return result[0]


async def get_time_trigger(user_id):
    async with aiosqlite.connect(wt_database) as conn:
        async with conn.cursor() as cursor:
            result = await cursor.execute("SELECT time_trigger FROM user WHERE user_id = ?",(user_id,))
            result = await result.fetchone()
            return result[0]


async def get_all_transactions_from_wallet(user_wallet, user_time_trigger):
    async with aiosqlite.connect(wallet_txs_database) as conn:
        async with conn.cursor() as cursor:
            current_time = int(time.time())
            time_interval = current_time - user_time_trigger
            result = await cursor.execute("SELECT transaction_hash, wallet_address, contract_address, value, coin, timestamp "
                                          "FROM wallets_transactions "
                                          "WHERE wallet_address = ? "
                                          "AND CAST(timestamp AS INTEGER) >= ?",(user_wallet, time_interval,))
            txs_list = list()
            result = await result.fetchall()
            txs_list = [tx for tx in result if tx not in txs_list]
            return txs_list


async def mark_transactions_as_notified(transaction_hashes, user_id):
    async with aiosqlite.connect(wallet_txs_database) as conn:
        async with conn.cursor() as cursor:
            for tx_hash in transaction_hashes:
                await cursor.execute("""
                    SELECT notified FROM wallets_transactions
                    WHERE transaction_hash = ?
                """, (tx_hash,))
                row = await cursor.fetchone()
                if row:
                    new_user_list = f"{row[0]}{user_id}:"
                    await cursor.execute("""
                        UPDATE wallets_transactions
                        SET notified = ?
                        WHERE transaction_hash = ?
                    """, (new_user_list, tx_hash))
            await conn.commit()


async def get_tx_notified_list(tx_hash):
    async with aiosqlite.connect(wallet_txs_database) as conn:
        async with conn.cursor() as cursor:
            result = await cursor.execute("SELECT notified FROM wallets_transactions WHERE transaction_hash = ?", (tx_hash,))
            result = await result.fetchone()
            return [i for i in result[0].split(":") if len(i) > 0]


async def get_all_tracking_wallets():
    async with aiosqlite.connect(wt_database) as conn:
        async with conn.cursor() as cursor:
            result = await cursor.execute("SELECT wallet_address FROM tracking_wallets")
            result = [i[0] for i in await result.fetchall() if len(i) > 0]
            final_list = list()
            final_list = [i for i in result if i not in final_list]
            return final_list


async def check_user_exists(user_id):
    async with aiosqlite.connect(wt_database) as conn:
        async with conn.cursor() as cursor:
            result = await cursor.execute("SELECT user_id FROM user WHERE user_id = ?", (user_id,))
            user = await result.fetchall()
        return bool(len(user))


async def add_user_to_db(user_id, username):
    async with aiosqlite.connect(wt_database) as conn:
        async with conn.cursor() as cursor:
            current_time = int(time.time())
            seconds_in_a_day = 24 * 60 * 60
            d_to_add = 1
            new_time = current_time + (d_to_add * seconds_in_a_day)
            await cursor.execute(
                "INSERT INTO user (user_id, username, active_task, sub_type, activity_time_check, tracking_wallets_limit, wallets_trigger_count, menu_status, time_trigger, activity_status) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (user_id, username, 0, 0, new_time, 10, 2, 0, 10, 1,))
            await conn.commit()


async def update_username(user_id, username):
    async with aiosqlite.connect(wt_database) as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("UPDATE user SET username = ? WHERE user_id = ?", (username, user_id,))
            await conn.commit()



async def update_activity_notification_time(user_id, next_activity_time_check):
    async with aiosqlite.connect(wt_database) as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("UPDATE user SET activity_time_check = ? WHERE user_id = ?", (next_activity_time_check, user_id,))
            await conn.commit()


async def get_activity_notification_time(user_id):
    async with aiosqlite.connect(wt_database) as conn:
        async with conn.cursor() as cursor:
            result = await cursor.execute("SELECT activity_time_check FROM user WHERE user_id = ?", (user_id,))
            user_status = await result.fetchone()
            return user_status[0]


async def change_user_menu_status(user_id, status):
    async with aiosqlite.connect(wt_database) as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("UPDATE user SET menu_status = ? WHERE user_id = ?", (status, user_id,))
            await conn.commit()


async def get_user_status(user_id):
    async with aiosqlite.connect(wt_database) as conn:
        async with conn.cursor() as cursor:
            result = await cursor.execute("SELECT menu_status FROM user WHERE user_id = ?", (user_id,))
            user_status = await result.fetchone()
            return user_status[0]


async def write_new_wallet_name(user_id, wallet_name):
    async with aiosqlite.connect(wt_database) as conn:
        async with conn.cursor() as cursor:
            all_wallets_unique_ids = await cursor.execute("SELECT wallet_id FROM tracking_wallets")
            all_wallets_unique_ids = [i[0] for i in await all_wallets_unique_ids.fetchall()]

            while True:
                unique_id = random.randrange(99, 999999999)
                if unique_id not in all_wallets_unique_ids:
                    break

            await cursor.execute(
                "INSERT INTO tracking_wallets (user_id, wallet_address, wallet_name, wallet_id, rename_status) VALUES(?, ?, ?, ?, ?)",
                (user_id, "", wallet_name, unique_id, 0,))

            await conn.commit()


async def update_wallet_address(user_id, wallet_address):
    async with aiosqlite.connect(wt_database) as conn:
        async with conn.cursor() as cursor:
            wallet_id = await cursor.execute("SELECT wallet_id FROM tracking_wallets WHERE wallet_address = ? AND user_id = ?", ("", user_id,))
            wallet_id = await wallet_id.fetchone()
            await cursor.execute("UPDATE tracking_wallets SET wallet_address = ? WHERE wallet_id = ?", (wallet_address, wallet_id[0],))
            await conn.commit()


async def update_wallet_name(wallet_name, wallet_id):
    async with aiosqlite.connect(wt_database) as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("UPDATE tracking_wallets SET wallet_name = ? WHERE wallet_id = ?", (wallet_name, wallet_id,))
            await conn.commit()


async def del_unused_wallet_address(user_id):
    async with aiosqlite.connect(wt_database) as conn:
        async with conn.cursor() as cursor:
            result = await cursor.execute("SELECT wallet_address, wallet_id FROM tracking_wallets WHERE user_id = ?", (user_id,))
            result = [i for i in await result.fetchall()]

            for wallet in result:
                if wallet[0] == "":
                    await cursor.execute("DELETE FROM tracking_wallets WHERE wallet_id = ?", (wallet[1],))

            await conn.commit()


async def fetch_wallets_from_db(user_id):
    async with aiosqlite.connect(wt_database) as conn:
        async with conn.cursor() as cursor:
            result = await cursor.execute("SELECT wallet_address, wallet_name, wallet_id FROM tracking_wallets WHERE user_id = ?", (user_id,))
            result = await result.fetchall()
            return result


async def rename_wallet_id_status(user_id, wallet_id, rename_status):
    async with aiosqlite.connect(wt_database) as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("UPDATE tracking_wallets SET rename_status = ? WHERE wallet_id = ?", (rename_status, wallet_id,))
            await conn.commit()


async def find_wallet_id_with_rename_status(user_id):
    async with aiosqlite.connect(wt_database) as conn:
        async with conn.cursor() as cursor:
            result = await cursor.execute("SELECT wallet_id FROM tracking_wallets WHERE user_id = ? AND rename_status = ?", (user_id, 1))
            result = await result.fetchone()
            return result[0]


async def get_wallet_info(wallet_id):
    async with aiosqlite.connect(wt_database) as conn:
        async with conn.cursor() as cursor:
            result = await cursor.execute("SELECT wallet_name, wallet_address FROM tracking_wallets WHERE wallet_id = ?", (wallet_id,))
            result = await result.fetchone()
            return result


async def get_wallet_name(wallet_address, user_id):
    async with aiosqlite.connect(wt_database) as conn:
        async with conn.cursor() as cursor:
            result = await cursor.execute("SELECT wallet_name FROM tracking_wallets WHERE wallet_address = ? AND user_id = ?", (wallet_address, user_id))
            result = await result.fetchone()
            return result[0]


async def delete_wallet_from_db(wallet_id):
    async with aiosqlite.connect(wt_database) as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("DELETE FROM tracking_wallets WHERE wallet_id = ?", (wallet_id,))
            await conn.commit()


async def update_wallet_trigger_count(user_id, trigger_count):
    async with aiosqlite.connect(wt_database) as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("UPDATE user SET wallets_trigger_count = ? WHERE user_id = ?", (trigger_count, user_id,))
            await conn.commit()


async def update_time_trigger(user_id, time_trigger):
    async with aiosqlite.connect(wt_database) as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("UPDATE user SET time_trigger = ? WHERE user_id = ?", (time_trigger, user_id,))
            await conn.commit()


async def check_user_sub_tier(user_id):
    async with aiosqlite.connect(wt_database) as conn:
        async with conn.cursor() as cursor:
            result = await cursor.execute("SELECT tracking_wallets_limit FROM user WHERE user_id = ?", (user_id,))
            result = await result.fetchone()
            return result[0]


async def get_current_users_wallet_number(user_id):
    async with aiosqlite.connect(wt_database) as conn:
        async with conn.cursor() as cursor:
            result = await cursor.execute("SELECT wallet_address FROM tracking_wallets WHERE user_id = ?", (user_id,))
            result = await result.fetchall()
            return [i[0] for i in result]


async def change_wallet_track_limit(tracking_wallet_limit, user_id):
    async with aiosqlite.connect(wt_database) as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("UPDATE user SET tracking_wallets_limit = ? WHERE user_id = ?", (tracking_wallet_limit, user_id,))
            await conn.commit()
