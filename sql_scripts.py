import sqlite3
from config import *


def admin_users():
    conn = sqlite3.connect(data_base)
    cursor = conn.cursor()

    cursor.execute("SELECT admin FROM admin_table")
    admins = cursor.fetchall()
    admins = [i[0] for i in admins]

    conn.close()

    return admins


def add_user_to_db(user_id, username):
    conn = sqlite3.connect(data_base)
    cursor = conn.cursor()

    cursor.execute("INSERT INTO user (user_id, username, rights, date_end_sub, active_task) VALUES(?, ?, ?, ?, ?)", (user_id, username, 0, None, 0,))

    conn.commit()
    conn.close()


def update_username(user_id, username):
    conn = sqlite3.connect(data_base)
    cursor = conn.cursor()

    cursor.execute("UPDATE user SET username = ? WHERE user_id = ?", (username, user_id,))

    conn.commit()
    conn.close()


def check_user_exists(user_id):
    conn = sqlite3.connect(data_base)
    cursor = conn.cursor()

    result = cursor.execute("SELECT user_id FROM user WHERE user_id = ?", (user_id,))
    user = bool(len(result.fetchall()))

    conn.close()

    return user


def user_id_by_username(username):
    conn = sqlite3.connect(data_base)
    cursor = conn.cursor()

    result = cursor.execute("SELECT user_id FROM user WHERE username = ?", (username,))
    user = result.fetchone()[0]

    conn.close()

    return user


def change_users_rights(username, rights, new_date, prem_status):
    conn = sqlite3.connect(data_base)
    cursor = conn.cursor()

    cursor.execute("UPDATE user SET rights = ?, date_end_sub = ?, prem_status = ? WHERE username = ?", (rights, new_date, prem_status, username,))

    conn.commit()
    conn.close()


def check_users_rights(user_id):
    conn = sqlite3.connect(data_base)
    cursor = conn.cursor()

    result = cursor.execute("SELECT rights FROM user WHERE user_id = ?", (user_id,))
    rights = result.fetchone()[0]

    conn.close()

    return rights


def get_list_of_users_with_rights():
    conn = sqlite3.connect(data_base)
    cursor = conn.cursor()

    result = cursor.execute("SELECT user_id FROM user WHERE prem_status = ?", (1,))
    users = result.fetchall()
    users = [i[0] for i in users if i != None]

    conn.close()

    return users


def users_end_sub_date(user_id):
    conn = sqlite3.connect(data_base)
    cursor = conn.cursor()

    result = cursor.execute("SELECT date_end_sub FROM user WHERE user_id = ?", (user_id,))
    end_sub_date = result.fetchone()[0]

    conn.close()

    return end_sub_date


def auto_demote_users(user_id):
    conn = sqlite3.connect(data_base)
    cursor = conn.cursor()

    cursor.execute("UPDATE user SET rights = ?, date_end_sub = ?, prem_status = ? WHERE user_id = ?", (0, '', 0, user_id,))

    conn.commit()
    conn.close()


def get_active_task_status(user_id):
    conn = sqlite3.connect(data_base)
    cursor = conn.cursor()

    result = cursor.execute("SELECT active_task FROM user WHERE user_id = ?", (user_id,))
    active_task_status = result.fetchone()[0]

    conn.close()

    return active_task_status


def change_active_task_status(status, user_id):
    conn = sqlite3.connect(data_base)
    cursor = conn.cursor()

    cursor.execute("UPDATE user SET active_task = ? WHERE user_id = ?", (status, user_id,))

    conn.commit()
    conn.close()


def get_hash_list():
    conn = sqlite3.connect(data_base)
    cursor = conn.cursor()

    result = cursor.execute("SELECT txs_hash FROM hash_list")
    txs_hash = result.fetchall()
    txs_hash_list = [i[0] for i in txs_hash if i != None]

    conn.close()

    return txs_hash_list


def txs_hash_append_in_bd(txs_hash, user_id, chat_link, channel_link):
    conn = sqlite3.connect(data_base)
    cursor = conn.cursor()

    cursor.execute("INSERT INTO hash_list (txs_hash, user_id, chat_link, channel_link) VALUES(?, ?, ?, ?)", (txs_hash, user_id, chat_link, channel_link,))

    conn.commit()
    conn.close()


def add_new_wallet_in_top_list(wallet, pnl_value):
    conn = sqlite3.connect(data_base)
    cursor = conn.cursor()

    cursor.execute("INSERT INTO top_pnl_wallets (wallet, pnl) VALUES(?, ?)",(wallet, pnl_value))

    conn.commit()
    conn.close()


def get_top_wallets_list():
    conn = sqlite3.connect(data_base)
    cursor = conn.cursor()

    result = cursor.execute("SELECT * FROM top_pnl_wallets ORDER BY pnl DESC")
    wallets_list = result.fetchall()

    conn.close()

    return wallets_list


def delete_all_wallets_from_db():
    conn = sqlite3.connect(data_base)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM top_pnl_wallets;")

    conn.commit()
    conn.close()


def make_all_active_task_by_status(status):
    conn = sqlite3.connect(data_base)
    cursor = conn.cursor()

    cursor.execute("UPDATE user SET active_task = ?", (status,))

    conn.commit()
    conn.close()


def make_auto_post_status(status):
    conn = sqlite3.connect(data_base)
    cursor = conn.cursor()

    cursor.execute("UPDATE auto_post SET auto_status = ? WHERE auto_task = ?", (status, "auto_task_status"))

    conn.commit()
    conn.close()


def get_auto_post_status():
    conn = sqlite3.connect(data_base)
    cursor = conn.cursor()

    result = cursor.execute("SELECT auto_status FROM auto_post WHERE auto_task = ?", ("auto_task_status",))
    result = result.fetchone()[0]

    conn.close()

    return result


def check_top_list_wallets():
    conn = sqlite3.connect(data_base)
    cursor = conn.cursor()

    result = cursor.execute("SELECT wallet FROM top_pnl_wallets")
    result = [i[0] for i in result.fetchall()]

    conn.close()

    return result


def get_weekly_top_post_date():
    conn = sqlite3.connect(data_base)
    cursor = conn.cursor()

    result = cursor.execute("SELECT post_time FROM weekly_top WHERE weekly_top_operation = ?", ("weekly_top_post",))
    post_date = result.fetchone()[0]

    conn.close()

    return post_date


def write_new_weekly_post_date(new_date):
    conn = sqlite3.connect(data_base)
    cursor = conn.cursor()

    cursor.execute("UPDATE weekly_top SET post_time = ? WHERE weekly_top_operation = ?", (new_date, "weekly_top_post",))

    conn.commit()
    conn.close()


def get_wallet_list():
    conn = sqlite3.connect(data_base)
    cursor = conn.cursor()

    result = cursor.execute("SELECT wallet FROM wallet_list")
    wallet_list = result.fetchall()
    wallet_list = [i[0].lower() for i in wallet_list]

    conn.close()

    return wallet_list


def add_wallet_to_wallets_db(wallet_address):
    conn = sqlite3.connect(data_base)
    cursor = conn.cursor()

    cursor.execute("INSERT INTO wallet_list (wallet, contracts, coins) VALUES(?, ?, ?)", (wallet_address.lower(), "", ""))

    conn.commit()
    conn.close()


def add_contract_to_wallet_list(wallet_address, contract_address, coin):
    conn = sqlite3.connect(data_base)
    cursor = conn.cursor()

    contract_list = cursor.execute("SELECT contracts FROM wallet_list WHERE LOWER(wallet) = LOWER(?)", (wallet_address,))
    bd_contracts = contract_list.fetchone()

    coin_list = cursor.execute("SELECT coins FROM wallet_list WHERE LOWER(wallet) = LOWER(?)", (wallet_address,))
    bd_coins = coin_list.fetchone()


    try:
        contracts = [i for i in bd_contracts[0].split(":") if len(i) > 0]
        coins = [i for i in bd_coins[0].split(":") if len(i) > 0]
    except:
        contracts = []
        coins = []

    if contract_address not in contracts:
        contracts.append("{}:".format(contract_address))
        new_contracts_list = ":".join(contracts)
        cursor.execute("UPDATE wallet_list SET contracts = ? WHERE LOWER(wallet) = LOWER(?)", (new_contracts_list, wallet_address,))


        coins.append("{}:".format(coin))
        new_coins_list = ":".join(coins)
        cursor.execute("UPDATE wallet_list SET coins = ? WHERE LOWER(wallet) = LOWER(?)", (new_coins_list, wallet_address,))

        conn.commit()

    conn.close()


def wallet_count_of_contracts(wallet_address):
    conn = sqlite3.connect(data_base)
    cursor = conn.cursor()

    contract_list = cursor.execute("SELECT contracts FROM wallet_list WHERE LOWER(wallet) = LOWER(?)", (wallet_address,))
    try:
        contracts = [i for i in contract_list.fetchone()[0].split(":") if len(i) > 0]
    except:
        contracts = []
    conn.close()

    return len(contracts)


def get_daily_top_post_date():
    conn = sqlite3.connect(data_base)
    cursor = conn.cursor()

    result = cursor.execute("SELECT post_time FROM weekly_top WHERE weekly_top_operation = ?", ("daily_top_post",))
    post_date = result.fetchone()[0]

    conn.close()

    return post_date


def write_new_daily_post_date(new_date):
    conn = sqlite3.connect(data_base)
    cursor = conn.cursor()

    cursor.execute("UPDATE weekly_top SET post_time = ? WHERE weekly_top_operation = ?", (new_date, "daily_top_post",))

    conn.commit()
    conn.close()


def get_top_daily_wallets_list():
    conn = sqlite3.connect(data_base)
    cursor = conn.cursor()

    result = cursor.execute("SELECT * FROM top_daily_pnl_wallets ORDER BY pnl DESC")
    wallets_list = result.fetchall()

    conn.close()

    return wallets_list


def delete_all_daily_wallets_from_db():
    conn = sqlite3.connect(data_base)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM top_daily_pnl_wallets;")

    conn.commit()
    conn.close()


def add_new_wallet_in_top_daily_list_nobanana(wallet, pnl_value):
    conn = sqlite3.connect(data_base)
    cursor = conn.cursor()

    cursor.execute("INSERT INTO top_daily_pnl_wallets (wallet, pnl) VALUES(?, ?)",(wallet, pnl_value))

    conn.commit()
    conn.close()


def check_top_daily_list_wallets():
    conn = sqlite3.connect(data_base)
    cursor = conn.cursor()

    result = cursor.execute("SELECT wallet FROM top_daily_pnl_wallets")
    result = [i[0] for i in result.fetchall()]

    conn.close()

    return result


def check_top_weekly_list_wallets():
    conn = sqlite3.connect(data_base)
    cursor = conn.cursor()

    result = cursor.execute("SELECT wallet FROM top_weekly_pnl_wallets")
    result = [i[0] for i in result.fetchall()]

    conn.close()

    return result


def add_new_wallet_in_top_weekly_list_nobanana(wallet, pnl_value):
    conn = sqlite3.connect(data_base)
    cursor = conn.cursor()

    cursor.execute("INSERT INTO top_weekly_pnl_wallets (wallet, pnl) VALUES(?, ?)",(wallet, pnl_value))

    conn.commit()
    conn.close()


def get_weekly_top_post_date_nobanana():
    conn = sqlite3.connect(data_base)
    cursor = conn.cursor()

    result = cursor.execute("SELECT post_time FROM weekly_top WHERE weekly_top_operation = ?", ("weekly_top_post_nobanana",))
    post_date = result.fetchone()[0]

    conn.close()

    return post_date


def write_new_weekly_post_date_nobanana(new_date):
    conn = sqlite3.connect(data_base)
    cursor = conn.cursor()

    cursor.execute("UPDATE weekly_top SET post_time = ? WHERE weekly_top_operation = ?", (new_date, "weekly_top_post_nobanana",))

    conn.commit()
    conn.close()


def get_top_weekly_wallets_list():
    conn = sqlite3.connect(data_base)
    cursor = conn.cursor()

    result = cursor.execute("SELECT * FROM top_weekly_pnl_wallets ORDER BY pnl DESC")
    wallets_list = result.fetchall()

    conn.close()

    return wallets_list


def delete_all_wallets_from_db_weekly_nobanana():
    conn = sqlite3.connect(data_base)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM top_weekly_pnl_wallets;")

    conn.commit()
    conn.close()


def all_active_subs():
    conn = sqlite3.connect(data_base)
    cursor = conn.cursor()

    result = cursor.execute("SELECT user_id, username, date_end_sub FROM user WHERE prem_status = ?",(1,))
    prem_users = result.fetchall()

    conn.close()

    return prem_users


def scanned_coins_and_contracts(wallet_address):
    conn = sqlite3.connect(data_base)
    cursor = conn.cursor()

    contract_list = cursor.execute("SELECT contracts FROM wallet_list WHERE LOWER(wallet) = LOWER(?)",(wallet_address,))
    contracts = [i for i in contract_list.fetchone()[0].split(":") if len(i) > 0]

    coin_list = cursor.execute("SELECT coins FROM wallet_list WHERE LOWER(wallet) = LOWER(?)", (wallet_address,))
    coins = [i for i in coin_list.fetchone()[0].split(':') if len(i) > 0]

    coin_contract = zip(contracts, coins)

    return coin_contract
