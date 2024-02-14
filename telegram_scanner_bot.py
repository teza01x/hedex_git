import asyncio
import time
import datetime
from telebot.async_telebot import AsyncTeleBot
from telebot.types import InlineKeyboardMarkup
from telebot import types
from config import *
from asc_cloud import *
from parser import *
from markdownv2 import *
from sql_scripts import *
from async_sql_scripts_wt import change_wallet_track_limit


bot = AsyncTeleBot(telegram_token)


@bot.message_handler(commands=['start'])
async def start(message):
    try:
        user_id = message.from_user.id
        username = message.from_user.username

        if not check_user_exists(user_id):
            try:
                add_user_to_db(user_id, username)
                await bot.send_message(user_id, "*Hello\, this is a Hedex Premium Bot\!*", parse_mode="MarkdownV2")
            except Exception as error:
                print(error)
        else:
            text = "*Hello\!*👋"
            try:
                await bot.send_message(message.chat.id, text=text, parse_mode="MarkdownV2")
            except Exception as error:
                print(error)
    except Exception as e:
        print(f"Error: {e}")


@bot.message_handler(commands=['subs'])
async def subs(message):
    try:
        user_id = message.from_user.id

        admins = admin_users()

        if user_id in admins:
            active_sub_data = all_active_subs()
            example = ["🔶 User_id 🔶 Username 🔶 Date_End_Sub 🔶"]
            for data in active_sub_data:
                example.append("{} 🔸 {} 🔸 {} ".format(data[0], "@" + str(data[1]), data[2].split(' ')[0]))
            text = "\n\n".join(example)
            await bot.send_message(message.chat.id, text=text)
        else:
            await bot.send_message(message.from_user.id, text="⛔️*You do not have permission to use this command\.*", parse_mode="MarkdownV2", reply_to_message_id=message.id)
    except Exception as e:
        print(f"Error: {e}")


@bot.message_handler(commands=['promote'])
async def promote(message):
    try:
        user_id = message.from_user.id

        admins = admin_users()

        if user_id in admins:
            try:
                text = message.text
                username = text.split(' ')[1]
                sub_type = text.split(' ')[2]
                user_id = user_id_by_username(username)

                if sub_type in ['bronze', 'silver', 'gold']:
                    current_date = datetime.datetime.now()
                    new_date = current_date + datetime.timedelta(days=3)

                    current_unix_time = int(time.time())
                    unix_time_plus_24_hours = current_unix_time + 86400

                    invite_link = await bot.create_chat_invite_link(private_group_id, expire_date=unix_time_plus_24_hours, member_limit=1)
                    invite_link = invite_link.invite_link

                    if sub_type == "bronze":
                        change_users_rights(username, 0, new_date, 1)
                        await change_wallet_track_limit(30, user_id)
                    elif sub_type == "silver":
                        change_users_rights(username, 1, new_date, 1)
                        await change_wallet_track_limit(70, user_id)
                    elif sub_type == "gold":
                        change_users_rights(username, 1, new_date, 1)
                        await change_wallet_track_limit(150, user_id)


                    text = f"👍**Congratulations, you have granted user `{username}` {sub_type.upper()} subscription for 3 days.**"
                    markdown_text = escape(text, flag=0)
                    await bot.send_message(message.chat.id, text=markdown_text, parse_mode="MarkdownV2")
                    try:
                        text_to_user = f"🔥**Congratulations! You have been granted {sub_type.upper()} subscription for 3 days.**\nPremium channel: {invite_link}\nWallet Tracker Bot: @HedexTrackerBot"
                        markdown_text_to_user = escape(text_to_user, flag=0)
                        await bot.send_message(user_id, text=markdown_text_to_user, parse_mode="MarkdownV2")
                    except:
                        pass
                else:
                    await bot.send_message(message.chat.id, text="⛔️The subscription type was specified incorrectly.\nSubscriptions: bronze, silver, gold.")
            except Exception as error:
                print(error)
                await bot.send_message(message.chat.id, text="⛔️*An error occurred during a promotion attempt\.*",parse_mode="MarkdownV2")
        else:
            await bot.send_message(message.from_user.id, text="⛔️*You do not have permission to use this command\.*", parse_mode="MarkdownV2", reply_to_message_id=message.id)
    except Exception as e:
        print(f"Error: {e}")


@bot.message_handler(commands=['demote'])
async def demote(message):
    try:
        user_id = message.from_user.id

        admins = admin_users()

        if user_id in admins:
            try:
                text = message.text
                username = text.split(' ')[1]
                user_id = user_id_by_username(username)
                auto_demote_users(user_id)
                await change_wallet_track_limit(10, user_id)
                await bot.ban_chat_member(private_group_id, user_id=user_id)
                await asyncio.sleep(0.5)
                await bot.unban_chat_member(private_group_id, user_id=user_id)
            except:
                print("Error manual demote user")
                await bot.send_message(message.chat.id, text="⛔️*An error occurred during a demotion attempt\.*", parse_mode="MarkdownV2")

            try:
                text = f"**You have taken away subscription from the user: `{username}`**"
                markdown_text = escape(text, flag=0)
                await bot.send_message(message.chat.id, text=markdown_text, parse_mode="MarkdownV2")
            except Exception as error:
                print(error)
                await bot.send_message(message.chat.id, text="⛔️*An error occurred during a demotion attempt\.*",parse_mode="MarkdownV2")
        else:
            await bot.send_message(message.from_user.id, text="⛔️*You do not have permission to use this command\.*", parse_mode="MarkdownV2", reply_to_message_id=message.id)
    except Exception as e:
        print(f"Error: {e}")


@bot.message_handler(commands=['scan'])
async def scan(message):
    user_id = message.from_user.id
    try:
        individual_rights = None

        admins = admin_users()
        try:
            individual_rights = check_users_rights(user_id)
        except:
            pass

        if (user_id in admins) or (individual_rights == 1):
            auto_post_status = get_auto_post_status()
            if auto_post_status == 0:
                active_task = get_active_task_status(user_id)
                if active_task == 0:
                    change_active_task_status(1, user_id)
                    text = message.text
                    wallet_address = text.split(' ')[1]
                    try:
                        await bot.send_message(message.chat.id, text="⚡️*Your request has been processed*⚡️, please wait for a response *\(≈30 seconds\)*\.", parse_mode="MarkdownV2", reply_to_message_id=message.id)

                        while True:
                            first_point_info = await first_pass_cycle(wallet_address)
                            if first_point_info == "busy":
                                await asyncio.sleep(5)
                            elif first_point_info[0] == "free":
                                result_private, result_standard = await first_point(first_point_info[1], wallet_address)
                                break
                        try:
                            markdown_text = escape(result_private, flag=0)
                            try:
                                await bot.send_message(message.chat.id, text=markdown_text, parse_mode="MarkdownV2", disable_web_page_preview=True)
                            except Exception as error:
                                print(error)
                            change_active_task_status(0, user_id)
                        except Exception as error:
                            print(error)
                    except Exception as error:
                        print(error)
                        change_active_task_status(0, user_id)
                        await bot.send_message(message.from_user.id,
                                               text="⛔️*Unfortunately there is no information available at this address\.*⛔️",
                                               parse_mode="MarkdownV2", reply_to_message_id=message.id)
                else:
                    await bot.send_message(message.chat.id,
                                           text="⚠️ *You already have an active task* ⚠️\nWait for it to complete and try again\.",
                                           parse_mode="MarkdownV2", reply_to_message_id=message.id)
            else:
                await bot.send_message(message.chat.id,
                                       text="☑️**The data is now being published to a private group\.**☑️\n🔸**Please wait until the bot finishes publishing and repeat your request\.**🔸",
                                       parse_mode="MarkdownV2", reply_to_message_id=message.id)
        else:
            await bot.send_message(message.from_user.id, text="⛔️*You do not have permission to use this command\. To use this command\, a paid subscription is required\.*", parse_mode="MarkdownV2", reply_to_message_id=message.id)
    except Exception as e:
        print(f"Error: {e}")
        change_active_task_status(0, user_id)


@bot.message_handler(commands=['contract'])
async def contract(message):
    user_id = message.from_user.id
    try:
        individual_rights = None

        admins = admin_users()
        try:
            individual_rights = check_users_rights(user_id)
        except:
            pass

        if (user_id in admins) or (individual_rights == 1):
            auto_post_status = get_auto_post_status()
            if auto_post_status == 0:
                active_task = get_active_task_status(user_id)
                if active_task == 0:
                    change_active_task_status(1, user_id)
                    text = message.text
                    contract_address = text.split(' ')[1]
                    try:
                        await bot.send_message(message.chat.id, text="⚡️*Your request has been processed*⚡️, please wait for a response *\(≈15 seconds\)*\.", parse_mode="MarkdownV2", reply_to_message_id=message.id)
                        while True:
                            second_point_info = await second_pass_cycle(contract_address)
                            if second_point_info == "busy":
                                await asyncio.sleep(5)
                            elif second_point_info[0] == "free":
                                result_private, result_standard = await second_point(second_point_info[1], contract_address)
                                break
                        try:
                            markdown_text = escape(result_private, flag=0)
                            try:
                                button_list0 = [
                                    types.InlineKeyboardButton("️Maestro 🎩", url=f"t.me/maestro?start={contract_address}-hedexbot"),
                                ]
                                button_list1 = [
                                    types.InlineKeyboardButton("️Maestro Pro 🎩✨", url=f"t.me/MaestroProBot?start={contract_address}-hedexbot"),
                                    types.InlineKeyboardButton("️Banana Gun 🍌🔫", url=f"https://t.me/BananaGunSniper_bot?start=snp_Hedexbot_{contract_address}"),
                                ]
                                button_list2 = [
                                    types.InlineKeyboardButton("️Otto Scan 🔎", url=f"https://t.me/OttoSimBot?start={contract_address}"),
                                    types.InlineKeyboardButton("️Safe Analyzer 🔎", url=f"t.me/SafeAnalyzerbot?start={contract_address}"),
                                ]
                                button_list3 = [
                                    types.InlineKeyboardButton("️TTF Scan 🔎", url=f"https://t.me/ttfbotbot?start={contract_address}"),
                                    types.InlineKeyboardButton("️TTF Chart 📈", url=f"https://t.me/ttfbotbot?start=chart{contract_address}"),
                                ]

                                reply_markup = types.InlineKeyboardMarkup([button_list0, button_list1, button_list2, button_list3])

                                await bot.send_message(message.chat.id, text=markdown_text, parse_mode="MarkdownV2", reply_markup=reply_markup, disable_web_page_preview=True)
                            except Exception as error:
                                print(error)
                            change_active_task_status(0, user_id)
                        except Exception as error:
                            print(error)
                    except Exception as error:
                        print(error)
                        change_active_task_status(0, user_id)
                        await bot.send_message(message.from_user.id,
                                               text="⛔️*Unfortunately there is no information available at this address\.*⛔️",
                                               parse_mode="MarkdownV2", reply_to_message_id=message.id)
                else:
                    await bot.send_message(message.chat.id,
                                           text="⚠️ *You already have an active task* ⚠️\nWait for it to complete and try again\.",
                                           parse_mode="MarkdownV2", reply_to_message_id=message.id)
            else:
                await bot.send_message(message.chat.id,
                                       text="☑️**The data is now being published to a private group\.**☑️\n🔸**Please wait until the bot finishes publishing and repeat your request\.**🔸",
                                       parse_mode="MarkdownV2", reply_to_message_id=message.id)
        else:
            await bot.send_message(message.from_user.id, text="⛔️*You do not have permission to use this command\. To use this command\, a paid subscription is required\.*", parse_mode="MarkdownV2", reply_to_message_id=message.id)
    except Exception as e:
        print(f"Error: {e}")
        change_active_task_status(0, user_id)


@bot.message_handler(commands=['top25k'])
async def top25(message):
    user_id = message.from_user.id
    try:
        individual_rights = None

        admins = admin_users()
        try:
            individual_rights = check_users_rights(user_id)
        except:
            pass

        if (user_id in admins) or (individual_rights == 1):
            auto_post_status = get_auto_post_status()
            if auto_post_status == 0:
                active_task = get_active_task_status(user_id)
                if active_task == 0:
                    change_active_task_status(1, user_id)
                    try:
                        await bot.send_message(message.chat.id, text="⚡️*Your request has been processed*⚡️, please wait for a response *\(≈10 seconds\)*\.", parse_mode="MarkdownV2", reply_to_message_id=message.id)
                        while True:
                            url = "https://dexscreener.com/gainers?chainIds=ethereum&maxLiq=25000&min24HTxns=300&min24HSells=30&min24HVol=25000"
                            third_point_info = await third_pass_cycle(url)
                            if third_point_info == "busy":
                                await asyncio.sleep(20)
                            elif third_point_info[0] == "free":
                                result_private, result_standard = await third_point(third_point_info[1], 1)
                                break
                        try:
                            markdown_text = escape(result_private, flag=0)
                            try:
                                await bot.send_message(message.chat.id, text=markdown_text, parse_mode="MarkdownV2", disable_web_page_preview=True)
                            except Exception as error:
                                print(error)
                            change_active_task_status(0, user_id)
                        except Exception as error:
                            print(error)
                    except Exception as error:
                        print(error)
                        change_active_task_status(0, user_id)
                        await bot.send_message(message.from_user.id, text="⛔️*Unfortunately there is no information available at this address\.*⛔️", parse_mode="MarkdownV2", reply_to_message_id=message.id)
                else:
                    await bot.send_message(message.chat.id,
                                           text="⚠️ *You already have an active task* ⚠️\nWait for it to complete and try again\.",
                                           parse_mode="MarkdownV2", reply_to_message_id=message.id)
            else:
                await bot.send_message(message.chat.id,
                                       text="☑️**The data is now being published to a private group\.**☑️\n🔸**Please wait until the bot finishes publishing and repeat your request\.**🔸",
                                       parse_mode="MarkdownV2", reply_to_message_id=message.id)
        else:
            await bot.send_message(message.from_user.id, text="⛔️*You do not have permission to use this command\. To use this command\, a paid subscription is required\.*", parse_mode="MarkdownV2", reply_to_message_id=message.id)
    except Exception as e:
        print(f"Error: {e}")
        change_active_task_status(0, user_id)


@bot.message_handler(commands=['top50k'])
async def top50(message):
    user_id = message.from_user.id
    try:
        individual_rights = None

        admins = admin_users()
        try:
            individual_rights = check_users_rights(user_id)
        except:
            pass

        if (user_id in admins) or (individual_rights == 1):
            auto_post_status = get_auto_post_status()
            if auto_post_status == 0:
                active_task = get_active_task_status(user_id)
                if active_task == 0:
                    change_active_task_status(1, user_id)
                    try:
                        await bot.send_message(message.chat.id, text="⚡️*Your request has been processed*⚡️, please wait for a response *\(≈10 seconds\)*\.", parse_mode="MarkdownV2", reply_to_message_id=message.id)
                        while True:
                            url = "https://dexscreener.com/gainers?chainIds=ethereum&minLiq=25000&maxLiq=50000&min24HTxns=300&min24HSells=30&min24HVol=50000"
                            third_point_info = await third_pass_cycle(url)
                            if third_point_info == "busy":
                                await asyncio.sleep(20)
                            elif third_point_info[0] == "free":
                                result_private, result_standard = await third_point(third_point_info[1], 2)
                                break
                        try:
                            markdown_text = escape(result_private, flag=0)
                            try:
                                await bot.send_message(message.chat.id, text=markdown_text, parse_mode="MarkdownV2", disable_web_page_preview=True)
                            except Exception as error:
                                print(error)
                            change_active_task_status(0, user_id)
                        except Exception as error:
                            print(error)
                    except Exception as error:
                        print(error)
                        change_active_task_status(0, user_id)
                        await bot.send_message(message.from_user.id, text="⛔️*Unfortunately there is no information available at this address\.*⛔️", parse_mode="MarkdownV2", reply_to_message_id=message.id)
                else:
                    await bot.send_message(message.chat.id,
                                           text="⚠️ *You already have an active task* ⚠️\nWait for it to complete and try again\.",
                                           parse_mode="MarkdownV2", reply_to_message_id=message.id)
            else:
                await bot.send_message(message.chat.id,
                                       text="☑️**The data is now being published to a private group\.**☑️\n🔸**Please wait until the bot finishes publishing and repeat your request\.**🔸",
                                       parse_mode="MarkdownV2", reply_to_message_id=message.id)
        else:
            await bot.send_message(message.from_user.id, text="⛔️*You do not have permission to use this command\. To use this command\, a paid subscription is required\.*", parse_mode="MarkdownV2", reply_to_message_id=message.id)
    except Exception as e:
        print(f"Error: {e}")
        change_active_task_status(0, user_id)


@bot.message_handler(commands=['top100k'])
async def top100(message):
    user_id = message.from_user.id
    try:
        individual_rights = None

        admins = admin_users()
        try:
            individual_rights = check_users_rights(user_id)
        except:
            pass

        if (user_id in admins) or (individual_rights == 1):
            auto_post_status = get_auto_post_status()
            if auto_post_status == 0:
                active_task = get_active_task_status(user_id)
                if active_task == 0:
                    change_active_task_status(1, user_id)
                    try:
                        await bot.send_message(message.chat.id, text="⚡️*Your request has been processed*⚡️, please wait for a response *\(≈10 seconds\)*\.", parse_mode="MarkdownV2", reply_to_message_id=message.id)
                        while True:
                            url = "https://dexscreener.com/gainers?chainIds=ethereum&minLiq=50000&maxLiq=100000&min24HTxns=300&min24HSells=30&min24HVol=100000"
                            third_point_info = await third_pass_cycle(url)
                            if third_point_info == "busy":
                                await asyncio.sleep(20)
                            elif third_point_info[0] == "free":
                                result_private, result_standard = await third_point(third_point_info[1], 3)
                                break
                        try:
                            markdown_text = escape(result_private, flag=0)
                            try:
                                await bot.send_message(message.chat.id, text=markdown_text, parse_mode="MarkdownV2", disable_web_page_preview=True)
                            except Exception as error:
                                print(error)
                            change_active_task_status(0, user_id)
                        except Exception as error:
                            print(error)
                    except Exception as error:
                        print(error)
                        change_active_task_status(0, user_id)
                        await bot.send_message(message.from_user.id, text="⛔️*Unfortunately there is no information available at this address\.*⛔️", parse_mode="MarkdownV2", reply_to_message_id=message.id)
                else:
                    await bot.send_message(message.chat.id,
                                           text="⚠️ *You already have an active task* ⚠️\nWait for it to complete and try again\.",
                                           parse_mode="MarkdownV2", reply_to_message_id=message.id)
            else:
                await bot.send_message(message.chat.id,
                                       text="☑️**The data is now being published to a private group\.**☑️\n🔸**Please wait until the bot finishes publishing and repeat your request\.**🔸",
                                       parse_mode="MarkdownV2", reply_to_message_id=message.id)
        else:
            await bot.send_message(message.from_user.id, text="⛔️*You do not have permission to use this command\. To use this command\, a paid subscription is required\.*", parse_mode="MarkdownV2", reply_to_message_id=message.id)
    except Exception as e:
        print(f"Error: {e}")
        change_active_task_status(0, user_id)


@bot.message_handler(commands=['top250k'])
async def top250(message):
    user_id = message.from_user.id
    try:
        individual_rights = None

        admins = admin_users()
        try:
            individual_rights = check_users_rights(user_id)
        except:
            pass

        if (user_id in admins) or (individual_rights == 1):
            auto_post_status = get_auto_post_status()
            if auto_post_status == 0:
                active_task = get_active_task_status(user_id)
                if active_task == 0:
                    change_active_task_status(1, user_id)
                    try:
                        await bot.send_message(message.chat.id, text="⚡️*Your request has been processed*⚡️, please wait for a response *\(≈10 seconds\)*\.", parse_mode="MarkdownV2", reply_to_message_id=message.id)
                        while True:
                            url = "https://dexscreener.com/gainers?chainIds=ethereum&minLiq=100000&maxLiq=250000&min24HTxns=300&min24HSells=30&min24HVol=250000"
                            third_point_info = await third_pass_cycle(url)
                            if third_point_info == "busy":
                                await asyncio.sleep(20)
                            elif third_point_info[0] == "free":
                                result_private, result_standard = await third_point(third_point_info[1], 4)
                                break
                        try:
                            markdown_text = escape(result_private, flag=0)
                            try:
                                await bot.send_message(message.chat.id, text=markdown_text, parse_mode="MarkdownV2", disable_web_page_preview=True)
                            except Exception as error:
                                print(error)
                            change_active_task_status(0, user_id)
                        except Exception as error:
                            print(error)
                    except Exception as error:
                        print(error)
                        change_active_task_status(0, user_id)
                        await bot.send_message(message.from_user.id, text="⛔️*Unfortunately there is no information available at this address\.*⛔️", parse_mode="MarkdownV2", reply_to_message_id=message.id)
                else:
                    await bot.send_message(message.chat.id,
                                           text="⚠️ *You already have an active task* ⚠️\nWait for it to complete and try again\.",
                                           parse_mode="MarkdownV2", reply_to_message_id=message.id)
            else:
                await bot.send_message(message.chat.id,
                                       text="☑️**The data is now being published to a private group\.**☑️\n🔸**Please wait until the bot finishes publishing and repeat your request\.**🔸",
                                       parse_mode="MarkdownV2", reply_to_message_id=message.id)
        else:
            await bot.send_message(message.from_user.id, text="⛔️*You do not have permission to use this command\. To use this command\, a paid subscription is required\.*", parse_mode="MarkdownV2", reply_to_message_id=message.id)
    except Exception as e:
        print(f"Error: {e}")
        change_active_task_status(0, user_id)


@bot.message_handler(commands=['top500k'])
async def top500(message):
    user_id = message.from_user.id
    try:
        individual_rights = None

        admins = admin_users()
        try:
            individual_rights = check_users_rights(user_id)
        except:
            pass

        if (user_id in admins) or (individual_rights == 1):
            auto_post_status = get_auto_post_status()
            if auto_post_status == 0:
                active_task = get_active_task_status(user_id)
                if active_task == 0:
                    change_active_task_status(1, user_id)
                    try:
                        await bot.send_message(message.chat.id, text="⚡️*Your request has been processed*⚡️, please wait for a response *\(≈10 seconds\)*\.", parse_mode="MarkdownV2", reply_to_message_id=message.id)
                        while True:
                            url = "https://dexscreener.com/gainers?chainIds=ethereum&minLiq=250000&maxLiq=500000&min24HTxns=300&min24HSells=30&min24HVol=500000"
                            third_point_info = await third_pass_cycle(url)
                            if third_point_info == "busy":
                                await asyncio.sleep(20)
                            elif third_point_info[0] == "free":
                                result_private, result_standard = await third_point(third_point_info[1], 5)
                                break
                        try:
                            markdown_text = escape(result_private, flag=0)
                            try:
                                await bot.send_message(message.chat.id, text=markdown_text, parse_mode="MarkdownV2", disable_web_page_preview=True)
                            except Exception as error:
                                print(error)
                            change_active_task_status(0, user_id)
                        except Exception as error:
                            print(error)
                    except Exception as error:
                        print(error)
                        change_active_task_status(0, user_id)
                        await bot.send_message(message.from_user.id, text="⛔️*Unfortunately there is no information available at this address\.*⛔️", parse_mode="MarkdownV2", reply_to_message_id=message.id)
                else:
                    await bot.send_message(message.chat.id,
                                           text="⚠️ *You already have an active task* ⚠️\nWait for it to complete and try again\.",
                                           parse_mode="MarkdownV2", reply_to_message_id=message.id)
            else:
                await bot.send_message(message.chat.id,
                                       text="☑️**The data is now being published to a private group\.**☑️\n🔸**Please wait until the bot finishes publishing and repeat your request\.**🔸",
                                       parse_mode="MarkdownV2", reply_to_message_id=message.id)
        else:
            await bot.send_message(message.from_user.id, text="⛔️*You do not have permission to use this command\. To use this command\, a paid subscription is required\.*", parse_mode="MarkdownV2", reply_to_message_id=message.id)
    except Exception as e:
        print(f"Error: {e}")
        change_active_task_status(0, user_id)


@bot.message_handler(commands=['top1m'])
async def top1m(message):
    user_id = message.from_user.id
    try:
        individual_rights = None

        admins = admin_users()
        try:
            individual_rights = check_users_rights(user_id)
        except:
            pass

        if (user_id in admins) or (individual_rights == 1):
            auto_post_status = get_auto_post_status()
            if auto_post_status == 0:
                active_task = get_active_task_status(user_id)
                if active_task == 0:
                    change_active_task_status(1, user_id)
                    try:
                        await bot.send_message(message.chat.id, text="⚡️*Your request has been processed*⚡️, please wait for a response *\(≈10 seconds\)*\.", parse_mode="MarkdownV2", reply_to_message_id=message.id)
                        while True:
                            url = "https://dexscreener.com/gainers?chainIds=ethereum&minLiq=500000&maxLiq=1000000&min24HTxns=300&min24HSells=30&min24HVol=500000"
                            third_point_info = await third_pass_cycle(url)
                            if third_point_info == "busy":
                                await asyncio.sleep(20)
                            elif third_point_info[0] == "free":
                                result_private, result_standard = await third_point(third_point_info[1], 6)
                                break
                        try:
                            markdown_text = escape(result_private, flag=0)
                            try:
                                await bot.send_message(message.chat.id, text=markdown_text, parse_mode="MarkdownV2", disable_web_page_preview=True)
                            except Exception as error:
                                print(error)
                            change_active_task_status(0, user_id)
                        except Exception as error:
                            print(error)
                    except Exception as error:
                        print(error)
                        change_active_task_status(0, user_id)
                        await bot.send_message(message.from_user.id, text="⛔️*Unfortunately there is no information available at this address\.*⛔️", parse_mode="MarkdownV2", reply_to_message_id=message.id)
                else:
                    await bot.send_message(message.chat.id,
                                           text="⚠️ *You already have an active task* ⚠️\nWait for it to complete and try again\.",
                                           parse_mode="MarkdownV2", reply_to_message_id=message.id)
            else:
                await bot.send_message(message.chat.id,
                                       text="☑️**The data is now being published to a private group\.**☑️\n🔸**Please wait until the bot finishes publishing and repeat your request\.**🔸",
                                       parse_mode="MarkdownV2", reply_to_message_id=message.id)
        else:
            await bot.send_message(message.from_user.id, text="⛔️*You do not have permission to use this command\. To use this command\, a paid subscription is required\.*", parse_mode="MarkdownV2", reply_to_message_id=message.id)
    except Exception as e:
        print(f"Error: {e}")
        change_active_task_status(0, user_id)


@bot.message_handler(commands=['top2m'])
async def top2m(message):
    user_id = message.from_user.id
    try:
        individual_rights = None

        admins = admin_users()
        try:
            individual_rights = check_users_rights(user_id)
        except:
            pass

        if (user_id in admins) or (individual_rights == 1):
            auto_post_status = get_auto_post_status()
            if auto_post_status == 0:
                active_task = get_active_task_status(user_id)
                if active_task == 0:
                    change_active_task_status(1, user_id)
                    try:
                        await bot.send_message(message.chat.id, text="⚡️*Your request has been processed*⚡️, please wait for a response *\(≈10 seconds\)*\.", parse_mode="MarkdownV2", reply_to_message_id=message.id)
                        while True:
                            url = "https://dexscreener.com/gainers?chainIds=ethereum&minLiq=1000000&maxLiq=2000000&min24HTxns=300&min24HSells=30&min24HVol=500000"
                            third_point_info = await third_pass_cycle(url)
                            if third_point_info == "busy":
                                await asyncio.sleep(20)
                            elif third_point_info[0] == "free":
                                result_private, result_standard = await third_point(third_point_info[1], 7)
                                break
                        try:
                            markdown_text = escape(result_private, flag=0)
                            try:
                                await bot.send_message(message.chat.id, text=markdown_text, parse_mode="MarkdownV2", disable_web_page_preview=True)
                            except Exception as error:
                                print(error)
                            change_active_task_status(0, user_id)
                        except Exception as error:
                            print(error)
                    except Exception as error:
                        print(error)
                        change_active_task_status(0, user_id)
                        await bot.send_message(message.from_user.id, text="⛔️*Unfortunately there is no information available at this address\.*⛔️", parse_mode="MarkdownV2", reply_to_message_id=message.id)
                else:
                    await bot.send_message(message.chat.id,
                                           text="⚠️ *You already have an active task* ⚠️\nWait for it to complete and try again\.",
                                           parse_mode="MarkdownV2", reply_to_message_id=message.id)
            else:
                await bot.send_message(message.chat.id,
                                       text="☑️**The data is now being published to a private group\.**☑️\n🔸**Please wait until the bot finishes publishing and repeat your request\.**🔸",
                                       parse_mode="MarkdownV2", reply_to_message_id=message.id)
        else:
            await bot.send_message(message.from_user.id, text="⛔️*You do not have permission to use this command\. To use this command\, a `Individual` subscription is required\.*", parse_mode="MarkdownV2", reply_to_message_id=message.id)
    except Exception as e:
        print(f"Error: {e}")
        change_active_task_status(0, user_id)


@bot.message_handler(commands=['top5m'])
async def top5m(message):
    user_id = message.from_user.id
    try:
        individual_rights = None

        admins = admin_users()
        try:
            individual_rights = check_users_rights(user_id)
        except:
            pass

        if (user_id in admins) or (individual_rights == 1):
            auto_post_status = get_auto_post_status()
            if auto_post_status == 0:
                active_task = get_active_task_status(user_id)
                if active_task == 0:
                    change_active_task_status(1, user_id)
                    try:
                        await bot.send_message(message.chat.id, text="⚡️*Your request has been processed*⚡️, please wait for a response *\(≈10 seconds\)*\.", parse_mode="MarkdownV2", reply_to_message_id=message.id)
                        while True:
                            url = "https://dexscreener.com/gainers?chainIds=ethereum&minLiq=2000000&maxLiq=5000000&min24HTxns=300&min24HSells=30&min24HVol=500000"
                            third_point_info = await third_pass_cycle(url)
                            if third_point_info == "busy":
                                await asyncio.sleep(20)
                            elif third_point_info[0] == "free":
                                result_private, result_standard = await third_point(third_point_info[1], 8)
                                break
                        try:
                            markdown_text = escape(result_private, flag=0)
                            try:
                                await bot.send_message(message.chat.id, text=markdown_text, parse_mode="MarkdownV2", disable_web_page_preview=True)
                            except Exception as error:
                                print(error)
                            change_active_task_status(0, user_id)
                        except Exception as error:
                            print(error)
                    except Exception as error:
                        print(error)
                        change_active_task_status(0, user_id)
                        await bot.send_message(message.from_user.id, text="⛔️*Unfortunately there is no information available at this address\.*⛔️", parse_mode="MarkdownV2", reply_to_message_id=message.id)
                else:
                    await bot.send_message(message.chat.id,
                                           text="⚠️ *You already have an active task* ⚠️\nWait for it to complete and try again\.",
                                           parse_mode="MarkdownV2", reply_to_message_id=message.id)
            else:
                await bot.send_message(message.chat.id,
                                       text="☑️**The data is now being published to a private group\.**☑️\n🔸**Please wait until the bot finishes publishing and repeat your request\.**🔸",
                                       parse_mode="MarkdownV2", reply_to_message_id=message.id)
        else:
            await bot.send_message(message.from_user.id, text="⛔️*You do not have permission to use this command\. To use this command\, a `Individual` subscription is required\.*", parse_mode="MarkdownV2", reply_to_message_id=message.id)
    except Exception as e:
        print(f"Error: {e}")
        change_active_task_status(0, user_id)


async def auto_scan(wallet_address):
    while True:
        first_point_info = auto_first_pass_cycle(wallet_address)
        if first_point_info == "busy":
            await asyncio.sleep(20)
        elif first_point_info[0] == "free":
            wallet_age, trade_router, risk, scanned_before_str, new_header, new_body = await auto_first_point(first_point_info[1], wallet_address)
            break
    return wallet_age, trade_router, risk, scanned_before_str, new_header, new_body



async def auto_contract(contract_address):
    try:
        while True:
            second_point_info = auto_second_pass_cycle(contract_address)
            if second_point_info == "busy":
                await asyncio.sleep(20)
            elif second_point_info[0] == "free":
                wallet_info_list = await auto_second_point(second_point_info[1], contract_address)
                break
        return wallet_info_list
    except:
        return list()


async def auto_top(url, iteration):
    try:
        while True:
            third_point_info = auto_third_pass_cycle(url)
            if third_point_info == "busy":
                time.sleep(20)
            elif third_point_info[0] == "free":
                top_info, lp = await auto_third_point(third_point_info[1], iteration)
                break
        return top_info, lp
    except:
        return list(), str()


async def auto_posting_info():
    while True:
        try:
            off_driver_func()
            make_all_active_task_by_status(0)
            make_auto_post_status(1)
            await asyncio.sleep(1)
            liq_urls = [
                "https://dexscreener.com/gainers?chainIds=ethereum&maxLiq=25000&min24HTxns=300&min24HSells=30&min24HVol=25000",
                "https://dexscreener.com/gainers?chainIds=ethereum&minLiq=25000&maxLiq=50000&min24HTxns=300&min24HSells=30&min24HVol=50000",
                "https://dexscreener.com/gainers?chainIds=ethereum&minLiq=50000&maxLiq=100000&min24HTxns=300&min24HSells=30&min24HVol=100000",
                "https://dexscreener.com/gainers?chainIds=ethereum&minLiq=100000&maxLiq=250000&min24HTxns=300&min24HSells=30&min24HVol=250000",
                "https://dexscreener.com/gainers?chainIds=ethereum&minLiq=250000&maxLiq=500000&min24HTxns=300&min24HSells=30&min24HVol=500000",
                "https://dexscreener.com/gainers?chainIds=ethereum&minLiq=500000&maxLiq=1000000&min24HTxns=300&min24HSells=30&min24HVol=500000",
                "https://dexscreener.com/gainers?chainIds=ethereum&minLiq=1000000&maxLiq=2000000&min24HTxns=300&min24HSells=30&min24HVol=500000",
                "https://dexscreener.com/gainers?chainIds=ethereum&minLiq=2000000&maxLiq=5000000&min24HTxns=300&min24HSells=30&min24HVol=500000",
            ]
            iteration = 0
            for url in liq_urls:
                iteration += 1
                top_info, lp = await auto_top(url, iteration)
                print(f"ITERATION {iteration}")
                await asyncio.sleep(1)
                if len(top_info) == 0:
                    print("Error in auto_top block")
                else:
                    for contract_info in top_info[:3]:
                        percent_price_change = contract_info[0]
                        token_symbol = contract_info[1]
                        contract = contract_info[2]

                        wallet_info_list = await auto_contract(contract)
                        if len(wallet_info_list) == 0:
                            print("Error in auto_contract block")
                        else:
                            await asyncio.sleep(1)

                            contract_block = ("**TOP 3 WALLETS for** [{}](https://etherscan.io/token/{}) **({} + LP)**\n"
                                             "**{}:** [Dextools](https://www.dextools.io/app/en/ether/pair-explorer/{}) | [Dexscreener](https://dexscreener.com/ethereum/{})\n"
                                             "_____________________________\n\n".format(token_symbol, contract, lp, percent_price_change, contract, contract))

                            counter = 1
                            wallet_info_block = list()
                            wallet_info_block_lite = list()
                            for wallet_info in wallet_info_list[:3]:
                                wallet_trade_data = wallet_info[0]
                                wallet = wallet_info[1]

                                wallet_age, trade_router, risk, scanned_before_str, new_header, new_body = await auto_scan(wallet)

                                if counter == 1:
                                    perc_number = "1️⃣"
                                elif counter == 2:
                                    perc_number = "2️⃣"
                                elif counter == 3:
                                    perc_number = "3️⃣"

                                if len(new_body) == 0:
                                    new_body.append("N/A")

                                wallet_block = ("_________________\n"
                                                "{} `{}`[🔗](https://etherscan.io/address/{})\n"
                                                "👶 **Age:** {} **|** **Profitability:** {}\n"
                                                "🔎 **Scanned Before:** {}\n"
                                                "{}"
                                                "**{} PnL:**\n"
                                                "{}\n\n"
                                                "**TOTAL Stat:**\n"
                                                "{}\n\n"
                                                "**3 Highest Profit/ROI:**\n"
                                                "{}\n").format(perc_number, wallet, wallet, wallet_age, risk, scanned_before_str, trade_router, token_symbol, wallet_trade_data, "\n".join(new_header), "\n".join(new_body))
                                if counter == 1:
                                    wallet_block_lite = ("_________________\n"
                                                    "{} `{}`[🔗](https://etherscan.io/address/{})\n"
                                                    "👶 **Age:** {} **|** **Profitability:** {}\n"
                                                    "🔎 **Scanned Before:** {}\n"
                                                    "{}"
                                                    "**{} PnL:**\n"
                                                    "{}\n\n"
                                                    "**TOTAL Stat:**\n"
                                                    "{}\n\n"
                                                    "**3 Highest Profit/ROI:**\n"
                                                    "{}\n").format(perc_number, wallet, wallet, wallet_age, risk, scanned_before_str, trade_router, token_symbol, wallet_trade_data, "\n".join(new_header), "\n".join(new_body))
                                else:
                                    wallet_block_lite = ("_________________\n"
                                                    "{} [0x..(Premium Membership)](https://t.me/HedexPortalBot)\n"
                                                    "👶 **Age:** {} **|** **Profitability:** {}\n"
                                                    "🔎 **Scanned Before:** {}\n"
                                                    "{}"
                                                    "**{} PnL:**\n"
                                                    "{}\n\n"
                                                    "**TOTAL Stat:**\n"
                                                    "{}\n\n"
                                                    "**3 Highest Profit/ROI:**\n"
                                                    "{}\n").format(perc_number, wallet_age, risk, scanned_before_str, trade_router, token_symbol, wallet_trade_data, "\n".join(new_header), "\n".join(new_body))

                                wallet_info_block.append(wallet_block)
                                wallet_info_block_lite.append(wallet_block_lite)
                                counter += 1
                            button_list0 = [
                                types.InlineKeyboardButton("️Maestro 🎩", url=f"t.me/maestro?start={contract}-hedexbot"),
                            ]
                            button_list1 = [
                                types.InlineKeyboardButton("️Maestro Pro 🎩✨", url=f"t.me/MaestroProBot?start={contract}-hedexbot"),
                                types.InlineKeyboardButton("️Banana Gun 🍌🔫", url=f"https://t.me/BananaGunSniper_bot?start=snp_Hedexbot_{contract}"),
                            ]
                            button_list2 = [
                                types.InlineKeyboardButton("️Otto Scan 🔎", url=f"https://t.me/OttoSimBot?start={contract}"),
                                types.InlineKeyboardButton("️Safe Analyzer 🔎", url=f"t.me/SafeAnalyzerbot?start={contract}"),
                            ]
                            button_list3 = [
                                types.InlineKeyboardButton("️TTF Scan 🔎", url=f"https://t.me/ttfbotbot?start={contract}"),
                                types.InlineKeyboardButton("️TTF Chart 📈", url=f"https://t.me/ttfbotbot?start=chart{contract}"),
                            ]

                            reply_markup = types.InlineKeyboardMarkup([button_list0, button_list1, button_list2, button_list3])


                            signature = "\n⚡️ `Powered By Hedex` ⚡️\n🤖 @HedexPortalBot 🤖"
                            private_group_post = contract_block + "\n".join(wallet_info_block) + signature
                            private_group_post = escape(private_group_post, flag=0)

                            lite_group_post = contract_block + "\n".join(wallet_info_block_lite) + signature
                            lite_group_post = escape(lite_group_post, flag=0)

                            await bot.send_message(private_group_id, text=private_group_post, parse_mode="MarkdownV2", reply_markup=reply_markup, disable_web_page_preview=True)
                            await bot.send_message(standard_group_id, text=lite_group_post, parse_mode="MarkdownV2", reply_markup=reply_markup, disable_web_page_preview=True)
                make_all_active_task_by_status(0)
                make_auto_post_status(0)
                await asyncio.sleep(3600)
        except Exception as error:
            print(error)


async def check_users_sub_time():
    while True:
        try:
            individual_users = get_list_of_users_with_rights()

            for user_id in individual_users:
                get_users_end_sub_date = users_end_sub_date(user_id)

                end_sub_date = datetime.datetime.strptime(get_users_end_sub_date, "%Y-%m-%d %H:%M:%S.%f")
                current_date = datetime.datetime.now()

                if end_sub_date.date() == current_date.date() or end_sub_date < current_date:
                    try:
                        auto_demote_users(user_id)
                        await change_wallet_track_limit(10, user_id)
                    except:
                        print("Error demote user when sub is over")
                    try:
                        await bot.kick_chat_member(private_group_id, user_id=user_id)
                        # await bot.ban_chat_member(private_group_id, user_id=user_id)
                        # await bot.unban_chat_member(private_group_id, user_id=user_id)
                    except Exception as error:
                        print(f"Error to kick user: {user_id}")
                        print(error)
                    try:
                        text = ("**Your subscription has expired. To continue using the bot, renew your subscription!🙌**\n"
                                "@HedexPortalBot")
                        markdown_text = escape(text, flag=0)
                        await bot.send_message(user_id, text=markdown_text, parse_mode="MarkdownV2")
                    except:
                        pass
            await asyncio.sleep(10000)
        except Exception as error:
            print(error)


async def top10_pnl_wallets():


    def format_number_with_commas(number):
        formatted_number = "{:,.2f}".format(float(number))
        return formatted_number


    while True:
        try:
            post_date = get_weekly_top_post_date()
            current_date = datetime.datetime.now()
            if post_date == None:
                new_date = current_date + datetime.timedelta(days=days_delay_weekly)
                write_new_weekly_post_date(new_date)
            else:
                post_date_object = datetime.datetime.strptime(post_date, "%Y-%m-%d %H:%M:%S.%f")
                if post_date_object.date() == current_date.date() or post_date_object < current_date:
                    try:
                        wallets_list = get_top_wallets_list()
                        text = "️⚡️ **Weekly Top 10 - ✅ All**\n\n🔸 **The best traders found by Hedex over the last 7 days, the list includes absolutely all found traders.**\n🔸 **PNL - profitability of all transactions (profitable and unprofitable) in US dollars.**\n\n"
                        wallet_info = list()

                        for i in range(len(wallets_list)):
                            if i + 1 == 1:
                                wallet_info.append(f"🥇 **Wallet Address** ⬇️\n`{wallets_list[i][0]}`\n**💰 PnL: ${format_number_with_commas(wallets_list[i][1])}**\n[🔗 Etherscan](https://etherscan.io/address/{wallets_list[i][0]})\n")
                            elif i + 1 == 2:
                                wallet_info.append(f"🥈 **Wallet Address** ⬇️\n`{wallets_list[i][0]}`\n**💰 PnL: ${format_number_with_commas(wallets_list[i][1])}**\n[🔗 Etherscan](https://etherscan.io/address/{wallets_list[i][0]})\n")
                            elif i + 1 == 3:
                                wallet_info.append(f"🥉 **Wallet Address** ⬇️\n`{wallets_list[i][0]}`\n**💰 PnL: ${format_number_with_commas(wallets_list[i][1])}**\n[🔗 Etherscan](https://etherscan.io/address/{wallets_list[i][0]})\n")
                            elif i + 1 == 4:
                                wallet_info.append(f"4️⃣ **Wallet Address** ⬇️\n`{wallets_list[i][0]}`\n**💰 PnL: ${format_number_with_commas(wallets_list[i][1])}**\n[🔗 Etherscan](https://etherscan.io/address/{wallets_list[i][0]})\n")
                            elif i + 1 == 5:
                                wallet_info.append(f"5️⃣ **Wallet Address** ⬇️\n`{wallets_list[i][0]}`\n**💰 PnL: ${format_number_with_commas(wallets_list[i][1])}**\n[🔗 Etherscan](https://etherscan.io/address/{wallets_list[i][0]})\n")
                            elif i + 1 == 6:
                                wallet_info.append(f"6️⃣ **Wallet Address** ⬇️\n`{wallets_list[i][0]}`\n**💰 PnL: ${format_number_with_commas(wallets_list[i][1])}**\n[🔗 Etherscan](https://etherscan.io/address/{wallets_list[i][0]})\n")
                            elif i + 1 == 7:
                                wallet_info.append(f"7️⃣ **Wallet Address** ⬇️\n`{wallets_list[i][0]}`\n**💰 PnL: ${format_number_with_commas(wallets_list[i][1])}**\n[🔗 Etherscan](https://etherscan.io/address/{wallets_list[i][0]})\n")
                            elif i + 1 == 8:
                                wallet_info.append(f"8️⃣ **Wallet Address** ⬇️\n`{wallets_list[i][0]}`\n**💰 PnL: ${format_number_with_commas(wallets_list[i][1])}**\n[🔗 Etherscan](https://etherscan.io/address/{wallets_list[i][0]})\n")
                            elif i + 1 == 9:
                                wallet_info.append(f"9️⃣ **Wallet Address** ⬇️\n`{wallets_list[i][0]}`\n**💰 PnL: ${format_number_with_commas(wallets_list[i][1])}**\n[🔗 Etherscan](https://etherscan.io/address/{wallets_list[i][0]})\n")
                            elif i + 1 == 10:
                                wallet_info.append(f"🔟 **Wallet Address** ⬇️\n`{wallets_list[i][0]}`\n**💰 PnL: ${format_number_with_commas(wallets_list[i][1])}**\n[🔗 Etherscan](https://etherscan.io/address/{wallets_list[i][0]})\n")
                            else:
                                wallet_info.append(f"**Wallet Address** ⬇️\n`{wallets_list[i][0]}`\n**💰 PnL: ${format_number_with_commas(wallets_list[i][1])}**\n[🔗 Etherscan](https://etherscan.io/address/{wallets_list[i][0]})\n")

                        wallet_info_text = "\n".join(wallet_info[:10])

                        text = text + wallet_info_text + "\n⚡️ `Powered By Hedex` ⚡️\n🤖 @HedexPortalBot 🤖"
                        text = escape(text, flag=0)

                        try:
                            message_post = await bot.send_message(private_group_id, text=text, parse_mode="MarkdownV2", disable_web_page_preview=True)
                            await bot.pin_chat_message(private_group_id, message_post.id)
                            new_date = current_date + datetime.timedelta(days=days_delay_weekly)
                            write_new_weekly_post_date(new_date)
                            delete_all_wallets_from_db()
                        except Exception as error:
                            print("Error while posting TOP 10 weekly")
                            print(error)
                    except Exception as error:
                        print(error)
            await asyncio.sleep(25000)
        except Exception as error:
            print(error)


async def top_weekly_pnl_wallets():


    def format_number_with_commas(number):
        formatted_number = "{:,.2f}".format(float(number))
        return formatted_number


    while True:
        try:
            post_date = get_weekly_top_post_date_nobanana()
            current_date = datetime.datetime.now()
            if post_date == None:
                new_date = current_date + datetime.timedelta(days=days_delay_weekly)
                write_new_weekly_post_date_nobanana(new_date)
            else:
                post_date_object = datetime.datetime.strptime(post_date, "%Y-%m-%d %H:%M:%S.%f")
                if post_date_object.date() == current_date.date() or post_date_object < current_date:
                    try:
                        wallets_list = get_top_weekly_wallets_list()
                        text = "️⚡️ **Weekly Top 10 - ❌ Banana Gun** 🍌🔫\n\n🔸 **The best traders found by Hedex over the last 7 days, this list excludes Banana Gun Users.**\n🔸 **PNL - profitability of all transactions (profitable and unprofitable) in US dollars.**\n\n"
                        wallet_info = list()

                        for i in range(len(wallets_list)):
                            if i + 1 == 1:
                                wallet_info.append(f"🥇 **Wallet Address** ⬇️\n`{wallets_list[i][0]}`\n**💰 PnL: ${format_number_with_commas(wallets_list[i][1])}**\n[🔗 Etherscan](https://etherscan.io/address/{wallets_list[i][0]})\n")
                            elif i + 1 == 2:
                                wallet_info.append(f"🥈 **Wallet Address** ⬇️\n`{wallets_list[i][0]}`\n**💰 PnL: ${format_number_with_commas(wallets_list[i][1])}**\n[🔗 Etherscan](https://etherscan.io/address/{wallets_list[i][0]})\n")
                            elif i + 1 == 3:
                                wallet_info.append(f"🥉 **Wallet Address** ⬇️\n`{wallets_list[i][0]}`\n**💰 PnL: ${format_number_with_commas(wallets_list[i][1])}**\n[🔗 Etherscan](https://etherscan.io/address/{wallets_list[i][0]})\n")
                            elif i + 1 == 4:
                                wallet_info.append(f"4️⃣ **Wallet Address** ⬇️\n`{wallets_list[i][0]}`\n**💰 PnL: ${format_number_with_commas(wallets_list[i][1])}**\n[🔗 Etherscan](https://etherscan.io/address/{wallets_list[i][0]})\n")
                            elif i + 1 == 5:
                                wallet_info.append(f"5️⃣ **Wallet Address** ⬇️\n`{wallets_list[i][0]}`\n**💰 PnL: ${format_number_with_commas(wallets_list[i][1])}**\n[🔗 Etherscan](https://etherscan.io/address/{wallets_list[i][0]})\n")
                            elif i + 1 == 6:
                                wallet_info.append(f"6️⃣ **Wallet Address** ⬇️\n`{wallets_list[i][0]}`\n**💰 PnL: ${format_number_with_commas(wallets_list[i][1])}**\n[🔗 Etherscan](https://etherscan.io/address/{wallets_list[i][0]})\n")
                            elif i + 1 == 7:
                                wallet_info.append(f"7️⃣ **Wallet Address** ⬇️\n`{wallets_list[i][0]}`\n**💰 PnL: ${format_number_with_commas(wallets_list[i][1])}**\n[🔗 Etherscan](https://etherscan.io/address/{wallets_list[i][0]})\n")
                            elif i + 1 == 8:
                                wallet_info.append(f"8️⃣ **Wallet Address** ⬇️\n`{wallets_list[i][0]}`\n**💰 PnL: ${format_number_with_commas(wallets_list[i][1])}**\n[🔗 Etherscan](https://etherscan.io/address/{wallets_list[i][0]})\n")
                            elif i + 1 == 9:
                                wallet_info.append(f"9️⃣ **Wallet Address** ⬇️\n`{wallets_list[i][0]}`\n**💰 PnL: ${format_number_with_commas(wallets_list[i][1])}**\n[🔗 Etherscan](https://etherscan.io/address/{wallets_list[i][0]})\n")
                            elif i + 1 == 10:
                                wallet_info.append(f"🔟 **Wallet Address** ⬇️\n`{wallets_list[i][0]}`\n**💰 PnL: ${format_number_with_commas(wallets_list[i][1])}**\n[🔗 Etherscan](https://etherscan.io/address/{wallets_list[i][0]})\n")
                            else:
                                wallet_info.append(f"**Wallet Address** ⬇️\n`{wallets_list[i][0]}`\n**💰 PnL: ${format_number_with_commas(wallets_list[i][1])}**\n[🔗 Etherscan](https://etherscan.io/address/{wallets_list[i][0]})\n")

                        wallet_info_text = "\n".join(wallet_info[:10])

                        text = text + wallet_info_text + "\n⚡️ `Powered By Hedex` ⚡️\n🤖 @HedexPortalBot 🤖"
                        text = escape(text, flag=0)

                        try:
                            message_post = await bot.send_message(private_group_id, text=text, parse_mode="MarkdownV2", disable_web_page_preview=True)
                            await bot.pin_chat_message(private_group_id, message_post.id)
                            new_date = current_date + datetime.timedelta(days=days_delay_weekly)
                            write_new_weekly_post_date_nobanana(new_date)
                            delete_all_wallets_from_db_weekly_nobanana()
                        except Exception as error:
                            print("Error while posting TOP 10 weekly X Banana Gun")
                            print(error)
                    except Exception as error:
                        print(error)
            await asyncio.sleep(23000)
        except Exception as error:
            print(error)


async def top_daily_pnl_wallets():


    def format_number_with_commas(number):
        formatted_number = "{:,.2f}".format(float(number))
        return formatted_number


    while True:
        try:
            post_date = get_daily_top_post_date()
            current_date = datetime.datetime.now()
            if post_date == None:
                new_date = current_date + datetime.timedelta(days=days_delay_daily)
                write_new_daily_post_date(new_date)
            else:
                post_date_object = datetime.datetime.strptime(post_date, "%Y-%m-%d %H:%M:%S.%f")
                if post_date_object.date() == current_date.date() or post_date_object < current_date:
                    try:
                        wallets_list = get_top_daily_wallets_list()
                        text = "️⚡️ **Daily Top 10 - ❌ Banana Gun** 🍌🔫\n\n🔸 **The best traders found by Hedex over the last 24 Hours, this list excludes Banana Gun Users.**\n🔸 **PNL - profitability of all transactions (profitable and unprofitable) in US dollars.**\n\n"
                        wallet_info = list()

                        for i in range(len(wallets_list)):
                            if i + 1 == 1:
                                wallet_info.append(f"🥇 **Wallet Address** ⬇️\n`{wallets_list[i][0]}`\n**💰 PnL: ${format_number_with_commas(wallets_list[i][1])}**\n[🔗 Etherscan](https://etherscan.io/address/{wallets_list[i][0]})\n")
                            elif i + 1 == 2:
                                wallet_info.append(f"🥈 **Wallet Address** ⬇️\n`{wallets_list[i][0]}`\n**💰 PnL: ${format_number_with_commas(wallets_list[i][1])}**\n[🔗 Etherscan](https://etherscan.io/address/{wallets_list[i][0]})\n")
                            elif i + 1 == 3:
                                wallet_info.append(f"🥉 **Wallet Address** ⬇️\n`{wallets_list[i][0]}`\n**💰 PnL: ${format_number_with_commas(wallets_list[i][1])}**\n[🔗 Etherscan](https://etherscan.io/address/{wallets_list[i][0]})\n")
                            elif i + 1 == 4:
                                wallet_info.append(f"4️⃣ **Wallet Address** ⬇️\n`{wallets_list[i][0]}`\n**💰 PnL: ${format_number_with_commas(wallets_list[i][1])}**\n[🔗 Etherscan](https://etherscan.io/address/{wallets_list[i][0]})\n")
                            elif i + 1 == 5:
                                wallet_info.append(f"5️⃣ **Wallet Address** ⬇️\n`{wallets_list[i][0]}`\n**💰 PnL: ${format_number_with_commas(wallets_list[i][1])}**\n[🔗 Etherscan](https://etherscan.io/address/{wallets_list[i][0]})\n")
                            elif i + 1 == 6:
                                wallet_info.append(f"6️⃣ **Wallet Address** ⬇️\n`{wallets_list[i][0]}`\n**💰 PnL: ${format_number_with_commas(wallets_list[i][1])}**\n[🔗 Etherscan](https://etherscan.io/address/{wallets_list[i][0]})\n")
                            elif i + 1 == 7:
                                wallet_info.append(f"7️⃣ **Wallet Address** ⬇️\n`{wallets_list[i][0]}`\n**💰 PnL: ${format_number_with_commas(wallets_list[i][1])}**\n[🔗 Etherscan](https://etherscan.io/address/{wallets_list[i][0]})\n")
                            elif i + 1 == 8:
                                wallet_info.append(f"8️⃣ **Wallet Address** ⬇️\n`{wallets_list[i][0]}`\n**💰 PnL: ${format_number_with_commas(wallets_list[i][1])}**\n[🔗 Etherscan](https://etherscan.io/address/{wallets_list[i][0]})\n")
                            elif i + 1 == 9:
                                wallet_info.append(f"9️⃣ **Wallet Address** ⬇️\n`{wallets_list[i][0]}`\n**💰 PnL: ${format_number_with_commas(wallets_list[i][1])}**\n[🔗 Etherscan](https://etherscan.io/address/{wallets_list[i][0]})\n")
                            elif i + 1 == 10:
                                wallet_info.append(f"🔟 **Wallet Address** ⬇️\n`{wallets_list[i][0]}`\n**💰 PnL: ${format_number_with_commas(wallets_list[i][1])}**\n[🔗 Etherscan](https://etherscan.io/address/{wallets_list[i][0]})\n")
                            else:
                                wallet_info.append(f"**Wallet Address** ⬇️\n `{wallets_list[i][0]}`\n**💰 PnL: ${format_number_with_commas(wallets_list[i][1])}**\n[🔗 Etherscan](https://etherscan.io/address/{wallets_list[i][0]})\n")

                        wallet_info_text = "\n".join(wallet_info[:10])

                        text = text + wallet_info_text + "\n⚡️ `Powered By Hedex` ⚡️\n🤖 @HedexPortalBot 🤖"
                        text = escape(text, flag=0)

                        try:
                            message_post = await bot.send_message(private_group_id, text=text, parse_mode="MarkdownV2", disable_web_page_preview=True)
                            await bot.pin_chat_message(private_group_id, message_post.id)
                            new_date = current_date + datetime.timedelta(days=days_delay_daily)
                            write_new_daily_post_date(new_date)
                            delete_all_daily_wallets_from_db()
                        except Exception as error:
                            print("Error while posting TOP 10 daily")
                            print(error)
                    except Exception as error:
                        print(error)
            await asyncio.sleep(21000)
        except Exception as error:
            print(error)


async def main():
    try:
        bot_task = asyncio.create_task(bot.polling(non_stop=True, request_timeout=500))
        auto_top_post = asyncio.create_task(auto_posting_info())
        # sub_date_monitoring = asyncio.create_task(check_users_sub_time())
        # top_pnl_week_post = asyncio.create_task(top10_pnl_wallets())
        # top_pnl_daily_post = asyncio.create_task(top_daily_pnl_wallets())
        # top_pnl_weekly_post = asyncio.create_task(top_weekly_pnl_wallets())
        # await asyncio.gather(bot_task, sub_date_monitoring, auto_top_post, top_pnl_week_post, top_pnl_daily_post, top_pnl_weekly_post)
        await asyncio.gather(bot_task, auto_top_post)
    except Exception as error:
        print(error)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()
