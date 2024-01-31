import asyncio
import aiohttp
import time
import json
from goplus.token import Token
from telebot.types import InlineKeyboardMarkup
from telebot import types
from async_sql_scripts_wt import *


async def generate_wallets_keyboard(user_id, page=1, wallets_per_page=10):
    try:
        user_wallets = await fetch_wallets_from_db(user_id)

        start = (page - 1) * wallets_per_page
        end = start + wallets_per_page
        paginated_wallets = user_wallets[start:end]

        rows_of_buttons = []
        for wallet in paginated_wallets:
            wallet_name = wallet[1]
            wallet_id = wallet[2]
            wallet_buttons = [
                types.InlineKeyboardButton(wallet_name, callback_data=f"info_{wallet_id}"),
                types.InlineKeyboardButton("Rename", callback_data=f"rename_{wallet_id}"),
                types.InlineKeyboardButton("❌", callback_data=f"delete_{wallet_id}")
            ]
            rows_of_buttons.append(wallet_buttons)

        navigation_buttons = []
        if page > 1:
            navigation_buttons.append(types.InlineKeyboardButton("⬅️", callback_data=f"wallet_page_{page - 1}"))
        if end < len(user_wallets):
            navigation_buttons.append(types.InlineKeyboardButton("➡️", callback_data=f"wallet_page_{page + 1}"))

        if navigation_buttons:
            rows_of_buttons.append(navigation_buttons)

        return rows_of_buttons
    except Exception as error:
        print("Error in generate_wallets_keyboard func")
        print(error)


async def is_valid_string(s):
    return len(s) <= 8 and s.isalnum()


async def is_valid_crypto_wallet(wallet_address):
    correct_length = 42
    return wallet_address.startswith('0x') and len(wallet_address) == correct_length and ' ' not in wallet_address


async def format_number_with_commas(number):
    try:
        formatted_number = "{:,.2f}".format(float(number))
        return formatted_number
    except Exception as error:
        print("Error in format_number_with_commas func")

async def honeypot_api(contract_address):
    try:
        url = "https://api.honeypot.is/v2/IsHoneypot"
        headers = {}
        params = {
            "address": f"{contract_address}",
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params) as response:
                honeypot_response = await response.json()
                try:
                    total_holders = honeypot_response['token']['totalHolders']
                except:
                    total_holders = "N/A ⚠️"
                try:
                    ishoneypot = honeypot_response['honeypotResult']['isHoneypot']
                    if ishoneypot == True:
                        ishoneypot = "Yes 🔴"
                    elif ishoneypot == False:
                        ishoneypot = "No 🟢"
                except:
                    ishoneypot = "N/A ⚠️️"
                try:
                    red_flags = honeypot_response['flags']
                    red_flags = [i.replace("_", " ").capitalize() for i in red_flags]
                    if len(red_flags) == 0:
                        red_flags = "N/A ⚠️"
                    else:
                        red_flags = ", ".join(red_flags)
                except:
                    red_flags = "N/A ⚠️️"

                try:
                    buy_tax = honeypot_response['simulationResult']['buyTax']
                    buy_tax = round(float(buy_tax), 2)
                except:
                    buy_tax = "-"
                try:
                    sell_tax = honeypot_response['simulationResult']['sellTax']
                    sell_tax = round(float(sell_tax), 2)
                except:
                    sell_tax = "-"

                return "🐋 **Total Holders:** {}\n🍯 **HoneyPot:** {}\n🚩 **Red Flags:** {}\n⚖️ **Tax:** Buy {} % **|** Sell {} %".format(total_holders, ishoneypot, red_flags, buy_tax, sell_tax)
    except Exception as error:
        print("Error in honeypot_api func")
        print(error)
        return "🐋 **Total Holders:** N/A ⚠️\n🍯 **HoneyPot:** N/A ⚠️\n🚩 **Red Flags:** N/A ⚠️\n⚖️ **Tax:** Buy - % **|** Sell - %"


async def get_detailed_info(contract_address):
    async def format_token_info(data):
        if 'result' not in data or not data['result']:
            return "⚠️ **Token information not found.** ⚠️"

        formatted_info = ""
        for contract_address, info in data['result'].items():
            can_take_back_ownership_status = info.get('can_take_back_ownership')
            if can_take_back_ownership_status == '1':
                can_take_back_ownership = 'No 🚨'
            elif can_take_back_ownership_status == '0':
                can_take_back_ownership = 'Yes ✅'
            else:
                can_take_back_ownership = 'N/A ⚠️'
            formatted_info += f"🔱 **Renounced Ownership:** {can_take_back_ownership }\n"
            formatted_info += "—\n"
            formatted_info += f"📃 **Open CA:** {'Yes ✅' if info.get('is_open_source') == '1' else 'No ❌'}\n"
            formatted_info += f"⚙️ **Modifiable Trading Tax:** {'Yes 🚨' if info.get('slippage_modifiable') == '1' else 'N/A ⚠️'}\n"
            try:
                total_supply = info.get('total_supply')
                formatted_info += f"💠 **Total Supply:** {await format_number_with_commas(total_supply)}\n"
            except:
                formatted_info += f"💠 **Total Supply:** N/A ⚠️️\n"
            try:
                formatted_info += f"💳 **Creator Balance:** {await format_number_with_commas(float(info.get('creator_balance').split('.')[0]))} **|** {round(float(info.get('creator_percent')) * 100, 2)}%\n"
            except:
                formatted_info += f"💳 **Creator Balance:** N/A ⚠️️\n"
            # try:
            #     formatted_info += f"⚖️ **Supply % On Creator:** {round(float(info.get('creator_percent')) * 100, 2)}%\n"
            # except:
            #     formatted_info += f"⚖️ **Token Percent On Creator Balance:** N/A ⚠️️\n"
            formatted_info += f"🔒 **Liquidity Pool Holders:** {info.get('lp_holder_count', 'N/A ⚠️️')}\n"

        return formatted_info, float(total_supply)
    try:
        data = Token(access_token=None).token_security(
            chain_id="1", addresses=[f"{contract_address}"]
        )
        data_json = json.dumps(data.to_dict())
        data_dict = json.loads(data_json)
        return await format_token_info(data_dict)
    except Exception as error:
        print("Error in get_detailed_info_func")
        print(error)
        return "", 0
