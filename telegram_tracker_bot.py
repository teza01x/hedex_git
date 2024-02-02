import asyncio
import time
from telebot.async_telebot import AsyncTeleBot
from telebot.types import InlineKeyboardMarkup
from telebot import types
from datetime import datetime
from async_markdownv2 import *
from async_side_funcs import *
from async_sql_scripts_wt import *
from wt_config import *


bot = AsyncTeleBot(telegram_wt_token)


@bot.message_handler(commands=['start', 'menu'])
async def start(message):
    try:

        hedex_start_chat_id = -1002040787460
        hedex_start_channel_id = -1002001330347
        user_id = message.from_user.id
        username = message.from_user.username


        chat_type = message.chat.type
        if chat_type == 'private':
            chat_member = await bot.get_chat_member(hedex_start_chat_id, user_id)
            channel_member = await bot.get_chat_member(hedex_start_channel_id, user_id)
            if chat_member.status in ["creator", "administrator", "member"] and channel_member.status in ["creator", "administrator", "member"]:
                text = "*Greetings\!*\n*This is Hedex Wallet Tracker\!*\n*Here you can track your traders transactions using their blockchain wallets\.*"

                main_menu_text = ("Welcome to Hedex Wallet Tracker!\n"
                                  "From here you can add wallets to track and configure your notifications!\n\n"
                                  "More Information 👇\n\n"
                                  "[⚡️ Hedex Portal ⚡️](https://t.me/HedexPortalBot)")
                main_menu_text = await escape(main_menu_text, flag=0)

                button_list1 = [
                    types.InlineKeyboardButton("✨ Subscription ", callback_data="sub_propostion"),
                ]
                button_list2 = [
                    types.InlineKeyboardButton("➕ Add Wallet", callback_data="add_wallet"),
                    types.InlineKeyboardButton("⚙️ Configure", callback_data="configuration_menu"),
                ]
                button_list3 = [
                    types.InlineKeyboardButton("✍️ Manage", callback_data="wallet_page_1"),
                ]
                reply_markup = types.InlineKeyboardMarkup([button_list1, button_list2, button_list3])
                await bot.send_message(message.chat.id, text=main_menu_text, reply_markup=reply_markup, parse_mode="MarkdownV2", disable_web_page_preview=True)
            else:
                error_text = ("**Hey!👋**\n**It looks like you are new!**🆕\nTo use our tracking bot please join our Community by clicking the button below! 👇\n"
                              "Once you are a member of the Chat and have joined our information channel you’re good to go!\n")
                error_text = await escape(error_text, flag=0)

                button_list1 = [
                    types.InlineKeyboardButton("Hedex Chat 💬", url="https://t.me/hedexbotgateway"),
                ]
                button_list2 = [
                    types.InlineKeyboardButton("Hedex Info 📄", url="https://t.me/hedexbotinfo"),
                ]
                reply_markup = types.InlineKeyboardMarkup([button_list1, button_list2])
                await bot.send_message(message.chat.id, text=error_text, reply_markup=reply_markup, parse_mode="MarkdownV2", disable_web_page_preview=True)

            if not await check_user_exists(user_id):
                try:
                    await add_user_to_db(user_id, username)
                except Exception as error:
                    print(f"Error adding user to db error:\n{error}")
            else:
                await update_username(user_id, username)
    except Exception as e:
        print(f"Error in start message: {e}")


@bot.callback_query_handler(func=lambda call: True)
async def callback_query(call):
    user_id = call.message.chat.id


    if call.data.startswith("wallet_page_"):
        await bot.answer_callback_query(call.id)
        try:
            user_id = call.message.chat.id
            get_users_activity_status = await get_users_active_status(user_id)
            if get_users_activity_status == 2:
                current_time = int(time.time())
                seconds_in_a_day = 24 * 60 * 60
                d_to_add = 7
                next_activity_time_check = current_time + (d_to_add * seconds_in_a_day)

                await change_users_activity_status(user_id, 1)
                await update_activity_notification_time(user_id, next_activity_time_check)
            sub_tier = await check_user_sub_tier(user_id)
            current_wallet_list = await get_current_users_wallet_number(user_id)
            page = int(call.data.split("_")[-1])
            text = f"This is the wallet menu.\nHere you can delete, add and edit wallets.\nYou have used your wallets limit: {len(current_wallet_list)}/{sub_tier}"
            button_list = await generate_wallets_keyboard(user_id, page=page)

            button_list.insert(0, [types.InlineKeyboardButton("➕ Add New Wallet", callback_data="add_wallet")])
            button_list.append([types.InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_to_main_menu"), types.InlineKeyboardButton("Refresh 🔄", callback_data=f"wallet_page_{page}")])

            reply_markup = types.InlineKeyboardMarkup(button_list)

            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=reply_markup)
        except Exception as error:
            print(error)
    elif call.data == "add_wallet":
        await bot.answer_callback_query(call.id)
        user_id = call.message.chat.id
        sub_tier = await check_user_sub_tier(user_id)
        current_wallet_list = await get_current_users_wallet_number(user_id)
        current_wallet_count = len(current_wallet_list)
        if current_wallet_count >= sub_tier:
            text = f"You have reached the limit for adding wallets: {sub_tier}/{sub_tier}\nUpgrade your subscription level: @HedexPortalBot"

            button_list1 = [
                types.InlineKeyboardButton("🔙 Back", callback_data="wallet_page_1"),
            ]
            reply_markup = types.InlineKeyboardMarkup([button_list1])

            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=reply_markup)
        else:
            try:
                text = "Enter the wallet name. 8 characters. Only letters and numbers."

                button_list1 = [
                    types.InlineKeyboardButton("Cancel ❌", callback_data=f"cancel_add_wallet_stage_1"),
                ]
                reply_markup = types.InlineKeyboardMarkup([button_list1])

                await bot.send_message(chat_id=call.message.chat.id, text=text, reply_markup=reply_markup)
            except Exception as error:
                print(error)
            await change_user_menu_status(user_id, ENTER_WALLET_NAME_STATUS)

    elif call.data == "cancel_add_wallet_stage_1":
        await bot.answer_callback_query(call.id)
        try:
            await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
            await change_user_menu_status(user_id, BASIC_MENU_STATUS)
        except Exception as error:
            print(error)

    elif call.data == "back_to_main_menu":
        await bot.answer_callback_query(call.id)
        try:
            main_menu_text = ("Welcome to Hedex Wallet Tracker!\n"
                              "From here you can add wallets to track and configure your notifications!\n\n"
                              "More Information 👇\n\n"
                              "[⚡️ Hedex Portal ⚡️](https://t.me/HedexPortalBot)")
            main_menu_text = await escape(main_menu_text, flag=0)

            await change_user_menu_status(user_id, BASIC_MENU_STATUS)
            button_list1 = [
                types.InlineKeyboardButton("✨ Subscription ", callback_data="sub_propostion"),
            ]
            button_list2 = [
                types.InlineKeyboardButton("➕ Add Wallet", callback_data="add_wallet"),
                types.InlineKeyboardButton("⚙️ Configure", callback_data="configuration_menu"),
            ]
            button_list3 = [
                types.InlineKeyboardButton("✍️ Manage", callback_data="wallet_page_1"),
            ]
            reply_markup = types.InlineKeyboardMarkup([button_list1, button_list2, button_list3])

            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=main_menu_text, reply_markup=reply_markup, parse_mode="MarkdownV2", disable_web_page_preview=True)
        except Exception as error:
            print(error)

    elif call.data == "configuration_menu":
        await bot.answer_callback_query(call.id)
        try:
            text = ("Here you can adjust the amount of wallets that need to buy the same token and adjust the time between the purchases before a notification gets sent.\n"
                    "(Example 2 wallets need to buy the same token within 10 minutes)")
            button_list1 = [
                types.InlineKeyboardButton("🔘 Wallets Trigger", callback_data="wallets_trigger"),
            ]
            button_list2 = [
                types.InlineKeyboardButton("🕑 Time Trigger", callback_data="time_trigger"),
            ]
            button_list3 = [
                types.InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_to_main_menu"),
            ]
            reply_markup = types.InlineKeyboardMarkup([button_list1, button_list2, button_list3])

            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=reply_markup)
        except Exception as error:
            print(error)

    elif call.data == "time_trigger":
        await bot.answer_callback_query(call.id)
        try:
            text = "Please enter the time you wish the bot to track from the first purchase:"
            button_list1 = [
                types.InlineKeyboardButton("10 minutes", callback_data=f"time_trigger_{10}"),
                types.InlineKeyboardButton("30 minutes", callback_data=f"time_trigger_{30}"),
                types.InlineKeyboardButton("1 hour", callback_data=f"time_trigger_{60}"),
            ]
            button_list2 = [
                types.InlineKeyboardButton("2 hours", callback_data=f"time_trigger_{120}"),
                types.InlineKeyboardButton("3 hours", callback_data=f"time_trigger_{180}"),
                types.InlineKeyboardButton("6 hours", callback_data=f"time_trigger_{360}"),
            ]
            button_list3 = [
                types.InlineKeyboardButton("12 hours", callback_data=f"time_trigger_{720}"),
            ]
            button_list4 = [
                types.InlineKeyboardButton("🔙 Back", callback_data="configuration_menu"),
            ]
            reply_markup = types.InlineKeyboardMarkup([button_list1, button_list2, button_list3, button_list4])

            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=reply_markup)
        except Exception as error:
            print(error)

    elif call.data.startswith("time_trigger_"):
        await bot.answer_callback_query(call.id)
        time_trigger = int(call.data.split("_")[2])
        try:
            user_id = call.message.chat.id

            sub_tier = await check_user_sub_tier(user_id)
            if sub_tier == 10:
                text = ("Your subscription does not allow you to change this information.\nPlease upgrade your plan to Bronze or above to make full use of the customisation settings.\n"
                        "You can easily purchase a subscription through our bot: @HedexPortalBot")
                button_list1 = [
                    types.InlineKeyboardButton("🔙 Back", callback_data="time_trigger"),
                ]
                reply_markup = types.InlineKeyboardMarkup([button_list1])
                await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=reply_markup)
            else:
                await update_time_trigger(user_id, time_trigger)

                if 10 <= time_trigger <= 30:
                    text = f"Change accepted!\nNow time from the first purchase is: `{time_trigger} minutes`"
                elif time_trigger == 60:
                    text = f"Change accepted!\nNow time from the first purchase is: `{int(time_trigger/60)} hour`"
                elif 120 <= time_trigger <= 720:
                    text = f"Change accepted!\nNow time from the first purchase is: `{int(time_trigger/60)} hours`"
                text = await escape(text, flag=0)

                button_list1 = [
                    types.InlineKeyboardButton("🔙 Back", callback_data="time_trigger"),
                ]
                reply_markup = types.InlineKeyboardMarkup([button_list1])
                await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=reply_markup, parse_mode="MarkdownV2")

        except Exception as error:
            print(error)

    elif call.data == "wallets_trigger":
        await bot.answer_callback_query(call.id)
        try:
            text = "Please choose the amount of wallets that need to buy the same token before a notification:"

            button_list1 = [
                types.InlineKeyboardButton("2 wallets", callback_data=f"trigger_count_{2}"),
                types.InlineKeyboardButton("3 wallets", callback_data=f"trigger_count_{3}"),
                types.InlineKeyboardButton("4 wallets", callback_data=f"trigger_count_{4}"),
            ]
            button_list2 = [
                types.InlineKeyboardButton("5 wallets", callback_data=f"trigger_count_{5}"),
                types.InlineKeyboardButton("6 wallets", callback_data=f"trigger_count_{6}"),
                types.InlineKeyboardButton("7 wallets", callback_data=f"trigger_count_{7}"),
            ]
            button_list3 = [
                types.InlineKeyboardButton("8 wallets", callback_data=f"trigger_count_{8}"),
                types.InlineKeyboardButton("9 wallets", callback_data=f"trigger_count_{9}"),
                types.InlineKeyboardButton("10 wallets", callback_data=f"trigger_count_{10}"),
            ]
            button_list4 = [
                types.InlineKeyboardButton("🔙 Back", callback_data="configuration_menu"),
            ]
            reply_markup = types.InlineKeyboardMarkup([button_list1, button_list2, button_list3, button_list4])

            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=reply_markup)

        except Exception as error:
            print(error)

    elif call.data.startswith("trigger_count_"):
        await bot.answer_callback_query(call.id)
        trigger_count = call.data.split("_")[2]
        try:
            user_id = call.message.chat.id

            sub_tier = await check_user_sub_tier(user_id)
            if sub_tier == 10:
                text = ("Your subscription does not allow you to change this information.\nPlease upgrade your plan to Bronze or above to make full use of the customisation settings.\n"
                        "You can easily purchase a subscription through our bot: @HedexPortalBot")
                button_list1 = [
                    types.InlineKeyboardButton("🔙 Back", callback_data="wallets_trigger"),
                ]
                reply_markup = types.InlineKeyboardMarkup([button_list1])
                await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=reply_markup)
            else:
                await update_wallet_trigger_count(user_id, trigger_count)

                text = f"Change accepted!\nNow the amount of wallets that need to buy the same token before a notification: `{trigger_count} wallets`"
                text = await escape(text, flag=0)

                button_list1 = [
                    types.InlineKeyboardButton("🔙 Back", callback_data="wallets_trigger"),
                ]
                reply_markup = types.InlineKeyboardMarkup([button_list1])
                await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=reply_markup, parse_mode="MarkdownV2")
        except Exception as error:
            print(error)

    elif call.data == "sub_propostion":
        await bot.answer_callback_query(call.id)
        user_id = call.message.chat.id
        track_limit = await check_user_sub_tier(user_id)
        sub_tier, sub_info = limitations[track_limit][0], limitations[track_limit][1]
        try:
            text = ("Here you can manage your Hedex subscription.\n\n"
                    f"Your current subscription tier: {sub_tier}\n"
                    f"{sub_info}\n\n"
                    "If you wish to upgrade your subscription, check out our socials, join our free groups please click the portal button below:")

            button_list1 = [
                types.InlineKeyboardButton("⚡️ Hedex Portal ⚡️", url="https://t.me/HedexPortalBot"),
            ]
            button_list2 = [
                types.InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_to_main_menu"),
            ]
            reply_markup = types.InlineKeyboardMarkup([button_list1, button_list2])

            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,text=text, reply_markup=reply_markup)
        except Exception as erorr:
            print(error)

    elif call.data.startswith("cancel_rename_wallet_"):
        await bot.answer_callback_query(call.id)
        user_id = call.message.chat.id
        wallet_id = call.data.split("_")[3]
        try:
            await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
            await change_user_menu_status(user_id, BASIC_MENU_STATUS)
            await rename_wallet_id_status(user_id, wallet_id, 0)
        except Exception as error:
            print(error)

    elif call.data.startswith("rename_"):
        await bot.answer_callback_query(call.id)
        wallet_id = call.data.split("_")[1]
        text = "Enter the new wallet name. 8 characters. Only letters and numbers."
        button_list1 = [
            types.InlineKeyboardButton("Cancel ❌", callback_data=f"cancel_rename_wallet_{wallet_id}"),
        ]
        reply_markup = types.InlineKeyboardMarkup([button_list1])
        await bot.send_message(chat_id=call.message.chat.id, text=text, reply_markup=reply_markup)
        await change_user_menu_status(user_id, RENAME_WALLET_NAME_STATUS)
        await rename_wallet_id_status(user_id, wallet_id, 1)

    elif call.data.startswith("delete_"):
        await bot.answer_callback_query(call.id)
        wallet_id = call.data.split("_")[1]

        wallet_info = await get_wallet_info(wallet_id)

        text = f"Confirm that you want to delete this wallet:\nName: `{wallet_info[0]}`\nAddress: `{wallet_info[1]}`\n"
        text = await escape(text, flag=0)

        button_list1 = [
            types.InlineKeyboardButton("Confirm", callback_data=f"confirm_delete_{wallet_id}"),
            types.InlineKeyboardButton("Cancel", callback_data="cancel_delete"),
        ]
        reply_markup = types.InlineKeyboardMarkup([button_list1])

        await bot.send_message(chat_id=call.message.chat.id, text=text, reply_markup=reply_markup, parse_mode="MarkdownV2")

    elif call.data.startswith("info_"):
        await bot.answer_callback_query(call.id)
        wallet_id = call.data.split("_")[1]
        try:
            wallet_info = await get_wallet_info(wallet_id)
            text = f"Wallet info:\n\nName: {wallet_info[0]}\nAddress: {wallet_info[1]}\n"

            button_list1 = [
                types.InlineKeyboardButton("🔙 Back", callback_data="wallet_page_1"),
            ]
            reply_markup = types.InlineKeyboardMarkup([button_list1])
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=reply_markup)
        except Exception as error:
            print(error)

    elif call.data.startswith("confirm_delete_"):
        await bot.answer_callback_query(call.id)
        wallet_id = call.data.split("_")[2]
        await delete_wallet_from_db(wallet_id)
        try:
            await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        except Exception as e:
            print("An error occurred:", e)

    elif call.data == "cancel_delete":
        await bot.answer_callback_query(call.id)
        try:
            await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        except Exception as e:
            print("An error occurred:", e)

    elif call.data == "active":
        await bot.answer_callback_query(call.id)

        current_time = int(time.time())
        seconds_in_a_day = 24 * 60 * 60
        d_to_add = 7
        next_activity_time_check = current_time + (d_to_add * seconds_in_a_day)

        await change_users_activity_status(user_id, 1)
        await update_activity_notification_time(user_id, next_activity_time_check)
        await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)

    elif call.data == "not_active":
        await bot.answer_callback_query(call.id)
        await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)


@bot.message_handler(func=lambda message: True, content_types=['text'])
async def handle_text(message):
    chat_type = message.chat.type
    if chat_type == 'private':
        user_id = message.chat.id
        user_status = await get_user_status(user_id)

        if user_status == ENTER_WALLET_NAME_STATUS:
            text = "Enter trackable wallet address.\nThe wallet address starts with 0x..."

            wallet_name = message.text
            valid_status = await is_valid_string(wallet_name)
            if valid_status == True:
                await write_new_wallet_name(user_id, wallet_name)
                current_message_id = await bot.send_message(chat_id=message.chat.id, text=text)
                await change_user_menu_status(user_id, ENTER_WALLET_ADDRESS_STATUS)

                current_message_id = current_message_id.message_id
                msg1 = current_message_id - 1
                msg2 = current_message_id - 2
                try:
                    await bot.delete_message(chat_id=message.chat.id, message_id=msg1)
                    await bot.delete_message(chat_id=message.chat.id, message_id=msg2)
                except Exception as e:
                    print("An error occurred:", e)
            else:
                current_message_id = await bot.send_message(chat_id=message.chat.id, text="The name you entered does not meet the rules.\nEnter a name up to 8 characters long, consisting of letters or numbers")
                current_message_id = current_message_id.message_id
                msg1 = current_message_id - 1
                msg2 = current_message_id - 2
                try:
                    await bot.delete_message(chat_id=message.chat.id, message_id=msg1)
                    await bot.delete_message(chat_id=message.chat.id, message_id=msg2)
                except Exception as e:
                    print("An error occurred:", e)
        elif user_status == ENTER_WALLET_ADDRESS_STATUS:
            wallet_address = message.text
            valid_status = await is_valid_crypto_wallet(wallet_address)
            if valid_status == True:
                await update_wallet_address(user_id, wallet_address)

                current_message_id = message.id
                msg1 = current_message_id
                msg2 = current_message_id - 1
                try:
                    await bot.delete_message(chat_id=message.chat.id, message_id=msg1)
                    await bot.delete_message(chat_id=message.chat.id, message_id=msg2)
                except Exception as e:
                    print("An error occurred:", e)
                await del_unused_wallet_address(user_id)
                await change_user_menu_status(user_id, BASIC_MENU_STATUS)

                text = f"Congratulations! You have added a new wallet!\nWallet Address:\n`{wallet_address}`"
                text = await escape(text, flag=0)

                button_list1 = [
                    types.InlineKeyboardButton("✅", callback_data=f"cancel_delete"),
                ]
                reply_markup = types.InlineKeyboardMarkup([button_list1])

                await bot.send_message(chat_id=message.chat.id, text=text, reply_markup=reply_markup, parse_mode="MarkdownV2")
            else:
                current_message_id = await bot.send_message(chat_id=message.chat.id, text="The entered wallet does not meet the rules.\nEnter a valid blockchain wallet.")
                current_message_id = current_message_id.message_id
                msg1 = current_message_id - 1
                msg2 = current_message_id - 2
                try:
                    await bot.delete_message(chat_id=message.chat.id, message_id=msg1)
                    await bot.delete_message(chat_id=message.chat.id, message_id=msg2)
                except Exception as e:
                    print("An error occurred:", e)
        elif user_status == RENAME_WALLET_NAME_STATUS:
            wallet_name = message.text
            valid_status = await is_valid_string(wallet_name)
            if valid_status == True:
                wallet_id = await find_wallet_id_with_rename_status(user_id)
                await update_wallet_name(wallet_name, wallet_id)
                current_message_id = message.id
                msg1 = current_message_id
                msg2 = current_message_id - 1
                try:
                    await bot.delete_message(chat_id=message.chat.id, message_id=msg1)
                    await bot.delete_message(chat_id=message.chat.id, message_id=msg2)
                except Exception as e:
                    print("An error occurred:", e)
                await change_user_menu_status(user_id, BASIC_MENU_STATUS)
            else:
                current_message_id = await bot.send_message(chat_id=message.chat.id, text="The name you entered does not meet the rules.\nEnter a name up to 8 characters long, consisting of letters or numbers")
                current_message_id = current_message_id.message_id
                msg1 = current_message_id - 1
                msg2 = current_message_id - 2
                try:
                    await bot.delete_message(chat_id=message.chat.id, message_id=msg1)
                    await bot.delete_message(chat_id=message.chat.id, message_id=msg2)
                except Exception as e:
                    print("An error occurred:", e)


async def check_notification_condition():
    while True:
        try:
            all_users_id = await get_all_active_user_ids()

            for user_id in all_users_id:
                user_wallets_trigger_count = await get_wallets_trigger_count(user_id)
                user_time_trigger = await get_time_trigger(user_id) * 60
                all_users_wallets = await get_user_wallets(user_id)

                transactions_by_contract = {}

                for user_wallet in all_users_wallets:
                    wallet_txs = await get_all_transactions_from_wallet(user_wallet, user_time_trigger)
                    if len(wallet_txs) != 0:
                        for tx_hash, tx_wa, tx_ca, tx_value, tx_coin, tx_timestamp in wallet_txs:
                            check_tx_validity = await get_tx_notified_list(tx_hash)
                            if str(user_id) in check_tx_validity:
                                pass
                            else:
                                tx_timestamp = int(tx_timestamp)
                                if tx_ca not in transactions_by_contract:
                                    transactions_by_contract[tx_ca] = []
                                transactions_by_contract[tx_ca].append({
                                    'hash': tx_hash,
                                    'wallet': tx_wa,
                                    'contract_address': tx_ca,
                                    'value': tx_value,
                                    'coin': tx_coin,
                                    'timestamp': tx_timestamp
                                })

                if len(transactions_by_contract) != 0:
                    for contract_adr, transactions in transactions_by_contract.items():
                        unique_wallets = set(tx['wallet'] for tx in transactions)
                        if len(unique_wallets) >= user_wallets_trigger_count:
                            transactions.sort(key=lambda x: x['timestamp'])
                            if transactions[-1]['timestamp'] - transactions[0]['timestamp'] <= user_time_trigger:
                                header = list()
                                honeypot_data = await honeypot_api(transactions[0]['contract_address'])
                                detailed_contract_info, total_supply = await get_detailed_info(transactions[0]['contract_address'])
                                header_text = (f"🟢 **NEW BUYS** 🟢\n\n"
                                               f"🚨 {len(unique_wallets)} wallets within {int(user_time_trigger / 60)} minutes 🚨\n\n"
                                               f"📑 **CA:** [${transactions[0]['coin']}](https://etherscan.io/address/{transactions[0]['contract_address']})\n"
                                               f"`{transactions[0]['contract_address']}`\n"
                                               f"📊 **Chart:** [Dexscreener](https://dexscreener.com/ethereum/{transactions[0]['contract_address']}) | [DexTools](https://www.dextools.io/app/en/ether/pair-explorer/{transactions[0]['contract_address']})\n"
                                               f"—\n"
                                               f"**Token Scan:**\n"
                                               f"{honeypot_data}\n"
                                               f"{detailed_contract_info}\n"
                                               f"📍**Wallets:**\n")
                                header.append(header_text)

                                body = list()
                                transactions = list({frozenset(item.items()): item for item in transactions}.values())
                                for tx in transactions:
                                    time_str = datetime.utcfromtimestamp(tx['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
                                    time_obj = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
                                    formatted_time = time_obj.strftime("%H:%M:%S")
                                    formatted_date = time_obj.strftime("%d/%m/%Y")
                                    wallet_name = await get_wallet_name(tx['wallet'], user_id)
                                    bought_value = float(tx['value'])
                                    body_text = (f"🗣️ **Name:** [{wallet_name}](https://etherscan.io/address/{tx['wallet']})\n"
                                                 f"#️⃣ **THash:** [Etherscan](https://etherscan.io/tx/{tx['hash']})\n"
                                                 f"💰 **Bought:** {await format_number_with_commas(tx['value'])} {tx['coin']}\n"
                                                 f"🪙 **Bought Percent Supply:** {round((bought_value * 100) / total_supply, 2)}%\n"
                                                 f"⏱ **Time:** {formatted_time}\n"
                                                 f"📆 **Date:** {formatted_date}\n")
                                    body.append(body_text)
                                notification_alert = "{}{}\n[⚡️ Powered By Hedex ⚡️](https://t.me/HedexPortalBot)".format("\n".join(header), "—\n".join(body))
                                notification_alert = await escape(notification_alert, flag=0)
                                # print(notification_alert)
                                try:
                                    button_list0 = [
                                        types.InlineKeyboardButton("️Maestro 🎩", url=f"t.me/maestro?start={transactions[0]['contract_address']}-hedexbot"),
                                    ]
                                    button_list1 = [
                                        types.InlineKeyboardButton("️Maestro Pro 🎩✨", url=f"t.me/MaestroProBot?start={transactions[0]['contract_address']}-hedexbot"),
                                        types.InlineKeyboardButton("️Banana Gun 🍌🔫", url=f"https://t.me/BananaGunSniper_bot?start=snp_Hedexbot_{transactions[0]['contract_address']}"),
                                    ]
                                    button_list2 = [
                                        types.InlineKeyboardButton("️Otto Scan 🔎", url=f"https://t.me/OttoSimBot?start={transactions[0]['contract_address']}"),
                                        types.InlineKeyboardButton("️TTF Scan 🔎", url=f"https://t.me/ttfbotbot?start={transactions[0]['contract_address']}"),
                                    ]

                                    reply_markup = types.InlineKeyboardMarkup([button_list0, button_list1, button_list2])

                                    await bot.send_message(chat_id=user_id, text=notification_alert, reply_markup=reply_markup, parse_mode="MarkdownV2", disable_web_page_preview=True)
                                except Exception as error:
                                    print(error)
                                await mark_transactions_as_notified([tx['hash'] for tx in transactions], user_id)
            await asyncio.sleep(15)
            print("Check Done")
        except Exception as error:
            print(f"Error check_notification_condition func: {error}")


async def notification_activity_check():
    while True:
        all_users_id = await get_all_user_ids()

        for user_id in all_users_id:
            get_users_activity_status = await get_users_active_status(user_id)
            # 0 - active check noti, 1 - prove activity, 2 - noti sent, but user not active yet
            if get_users_activity_status == 0:
                text = "Greetings! Please confirm your activity status!"

                button_list0 = [
                    types.InlineKeyboardButton("️🟢", callback_data="active"),
                    types.InlineKeyboardButton("️🔴", callback_data="not_active"),
                ]

                reply_markup = types.InlineKeyboardMarkup([button_list0])
                try:
                    await bot.send_message(user_id, text=text, reply_markup=reply_markup)
                except:
                    pass
                await change_users_activity_status(user_id, 2)

        await asyncio.sleep(1)
        # await asyncio.sleep(120)


async def global_activity_check():
    while True:
        all_users_id = await get_all_user_ids()

        current_time = int(time.time())
        for user_id in all_users_id:
            activity_time = await get_activity_notification_time(user_id)

            if activity_time < current_time:
                await change_users_activity_status(user_id, 0)
                current_time = int(time.time())
                seconds_in_a_day = 24 * 60 * 60
                d_to_add = 30
                next_activity_time_check = current_time + (d_to_add * seconds_in_a_day)
                await update_activity_notification_time(user_id, next_activity_time_check)


        await asyncio.sleep(1)


async def main():
    try:
        bot_task = asyncio.create_task(bot.polling(non_stop=True, request_timeout=500))
        notification = asyncio.create_task(check_notification_condition())
        activity_notification = asyncio.create_task(notification_activity_check())
        global_activity_status_check = asyncio.create_task(global_activity_check())
        await asyncio.gather(bot_task, notification, activity_notification, global_activity_status_check)
    except Exception as error:
        print(error)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()
