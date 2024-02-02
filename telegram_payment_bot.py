import asyncio
import datetime
import time
from telebot.async_telebot import AsyncTeleBot
from telebot import types
from telebot.types import InlineKeyboardMarkup
from markdownv2 import *
from config import *
from sql_scripts import *
from blockchain import *
from async_sql_scripts_wt import change_wallet_track_limit


bot = AsyncTeleBot(payment_token)


@bot.message_handler(commands=['start', 'menu'])
async def start(message):

    chat_type = message.chat.type
    if chat_type == 'private':
        user_id = message.from_user.id
        username = message.from_user.username

        text = ("⚡️ Welcome to Hedex! ⚡️\n"
                "This is our Portal bot which will navigate you around the Hedex ecosystem!\n\n"
                "Hedex has been built to help traders to find and track alpha wallets, help our users become more profitable and make them more consistent traders!\n\n"
                "⁉️ What does Hedex offer?\n"
                "💎Deep wallet analysis on contracts and Ethereum wallets to give you the best Alpha Traders.\n"
                "⚙️Track wallets with full user customisation.\n"
                "🔎 Scan contracts to keep you safe!\n\n"
                "Our Socials:\n"
                "[Website](https://www.hedexbot.com) | [YouTube](https://youtube.com/@Hedexbot?si=veDXXwp2jtjaHH6o) | [Twitter (X)](https://x.com/hedexbot?s=21&t=4O7fqwfoOCUDViGWXA1J0w)")

        text = escape(text, flag=0)
        button_list1 = [
            types.InlineKeyboardButton("Subscribe 💠", callback_data="subscribe_menu"),
            types.InlineKeyboardButton("Free 🆓", callback_data="free_channel"),
        ]
        button_list2 = [
            types.InlineKeyboardButton("Information ℹ️", callback_data="information"),
            types.InlineKeyboardButton("Chat 💬", url="https://t.me/hedexbotgateway"),
        ]

        reply_markup = types.InlineKeyboardMarkup([button_list1, button_list2])


        if not check_user_exists(user_id):
            try:
                add_user_to_db(user_id, username)
                await bot.send_message(user_id, text="🤖")
                await bot.send_message(user_id, text=text, parse_mode="MarkdownV2", reply_markup=reply_markup, disable_web_page_preview=True)
            except Exception as error:
                print(error)
        else:
            try:
                update_username(user_id, username)
                await bot.send_message(message.chat.id, text=text, parse_mode="MarkdownV2", reply_markup=reply_markup, disable_web_page_preview=True)
            except Exception as error:
                print(error)


@bot.callback_query_handler(func=lambda call: True)
async def callback_query(call):
    if call.data == "subscribe_menu":
        await bot.answer_callback_query(call.id)
        text = ("**Hedex Subscriptions**\n"
                "We have a few options for subscribing to Hedex!\n"
                "If you’re just looking to find the best ETH wallets, get wallet analysis, wallet deep dives and to find the best traders of top performing tokens; then our **Premium Channel Subscription** is where you’ll find all that information!\n\n"
                "If you’re looking for all that AND to track wallets as well then sign up to either **Bronze, Silver or Gold!** These packages all come with access to our premium channel!\n\n"
                "For more information on all our subscriptions, you can find that [here](https://t.me/hedexbotinfo/17)\n"
                "Or sign up below 👇")

        text = escape(text, flag=0)

        button_list0 = [
            types.InlineKeyboardButton("Premium ⭐️", callback_data="premium"),
        ]
        button_list1 = [
            types.InlineKeyboardButton("Bronze 🟠", callback_data="bronze"),
            types.InlineKeyboardButton("Silver ⚪️", callback_data="silver"),
            types.InlineKeyboardButton("Gold 🟡", callback_data="gold"),
        ]
        button_list2 = [
            types.InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="back_to_main_menu"),
        ]
        reply_markup = types.InlineKeyboardMarkup([button_list0, button_list1, button_list2])

        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, parse_mode="MarkdownV2", reply_markup=reply_markup, disable_web_page_preview=True)

    elif call.data == "premium":
        await bot.answer_callback_query(call.id)
        text = ("⭐️ Premium:\n\n"
                "⚡️ Hedex Premium Channel ⚡️\n\n"
                "Our [Premium Channel](https://t.me/hedexbotinfo/17) has been created for a fully automated experience for users to find the best performing crypto’s and the very best Ethereum traders!\n"
                "To get an idea of what **Premium** can give you please check out [Lite Channel](https://t.me/HedexLite), this will give users an idea of the power but without the bells and whistles. (Lite users don’t get wallet addresses or Top 10 Daily and weekly traders)\n\n"
                "What to expect:\n"
                "- 24/7 Scans of top performing contracts\n"
                "- Find Alpha wallets\n"
                "- Profit & Loss of wallets\n"
                "- Fully automated experience\n\n"
                "For more information on what **Premium** can give you go [here](https://t.me/hedexbotinfo/17)"
                "**Payment Method: USDC | USDT | ETH**\n\n")
        text = escape(text, flag=0)

        ether_usdt_price = await get_eth_price()

        button_list0 = [
            types.InlineKeyboardButton(f"1 Month | {round(price_packages_usdt_usdc[1] / ether_usdt_price, 2)} ETH", callback_data=f"pay_sub_1_premium_{round(price_packages_usdt_usdc[1] / ether_usdt_price, 4)}"),
        ]
        button_list1 = [
            types.InlineKeyboardButton(f"3 Months | {round(price_packages_usdt_usdc[2] / ether_usdt_price, 2)} ETH", callback_data=f"pay_sub_2_premium_{round(price_packages_usdt_usdc[2] / ether_usdt_price, 4)}"),
        ]
        button_list2 = [
            types.InlineKeyboardButton(f"12 Months | {round(price_packages_usdt_usdc[3] / ether_usdt_price, 2)} ETH", callback_data=f"pay_sub_3_premium_{round(price_packages_usdt_usdc[3] / ether_usdt_price, 4)}"),
        ]
        button_list3 = [
            types.InlineKeyboardButton("⬅️ Back", callback_data="subscribe_menu"),
        ]
        reply_markup = types.InlineKeyboardMarkup([button_list0, button_list1, button_list2, button_list3])
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, parse_mode="MarkdownV2", reply_markup=reply_markup, disable_web_page_preview=True)

    elif call.data == "bronze":
        await bot.answer_callback_query(call.id)
        text = ("🟠 Bronze:\n\n"
                "🎯 Track up to 30 wallets\n"
                "⚙️ Full Notification Customisation\n"
                "🔎 Contract safe scan\n"
                "💎 Access to our Premium Wallet and Contact Analysis channel\n"
                "💰 Find Alpha wallets and traders with Premium access\n\n"
                "**Payment Method: USDC | USDT | ETH**\n\n")
        text = escape(text, flag=0)

        ether_usdt_price = await get_eth_price()

        button_list0 = [
            types.InlineKeyboardButton(f"1 Month | {round(price_packages_usdt_usdc[4] / ether_usdt_price, 2)} ETH", callback_data=f"pay_sub_4_bronze_{round(price_packages_usdt_usdc[4] / ether_usdt_price, 4)}"),
        ]
        button_list1 = [
            types.InlineKeyboardButton(f"3 Months | {round(price_packages_usdt_usdc[5] / ether_usdt_price, 2)} ETH", callback_data=f"pay_sub_5_bronze_{round(price_packages_usdt_usdc[5] / ether_usdt_price, 4)}"),
        ]
        button_list2 = [
            types.InlineKeyboardButton(f"12 Months | {round(price_packages_usdt_usdc[6] / ether_usdt_price, 2)} ETH", callback_data=f"pay_sub_6_bronze_{round(price_packages_usdt_usdc[6] / ether_usdt_price, 4)}"),
        ]
        button_list3 = [
            types.InlineKeyboardButton("⬅️ Back", callback_data="subscribe_menu"),
        ]
        reply_markup = types.InlineKeyboardMarkup([button_list0, button_list1, button_list2, button_list3])
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, parse_mode="MarkdownV2", reply_markup=reply_markup, disable_web_page_preview=True)

    elif call.data == "silver":
        await bot.answer_callback_query(call.id)
        text = ("⚪️ Silver:\n\n"
                "🎯 Track up to 70 wallets\n"
                "⚙️ Full Notification Customisation\n"
                "🔎 Contract safe scan\n"
                "💎 Access to our Premium Wallet and Contact Analysis channel\n"
                "💰 Find Alpha wallets and traders with Premium access\n\n"
                "**Payment Method: USDC | USDT | ETH**\n\n")
        text = escape(text, flag=0)

        ether_usdt_price = await get_eth_price()

        button_list0 = [
            types.InlineKeyboardButton(f"1 Month | {round(price_packages_usdt_usdc[7] / ether_usdt_price, 2)} ETH", callback_data=f"pay_sub_7_silver_{round(price_packages_usdt_usdc[7] / ether_usdt_price, 4)}"),
        ]
        button_list1 = [
            types.InlineKeyboardButton(f"3 Months | {round(price_packages_usdt_usdc[8] / ether_usdt_price, 2)} ETH", callback_data=f"pay_sub_8_silver_{round(price_packages_usdt_usdc[8] / ether_usdt_price, 4)}"),
        ]
        button_list2 = [
            types.InlineKeyboardButton(f"12 Months | {round(price_packages_usdt_usdc[9] / ether_usdt_price, 2)} ETH", callback_data=f"pay_sub_9_silver_{round(price_packages_usdt_usdc[9] / ether_usdt_price, 4)}"),
        ]
        button_list3 = [
            types.InlineKeyboardButton("⬅️ Back", callback_data="subscribe_menu"),
        ]
        reply_markup = types.InlineKeyboardMarkup([button_list0, button_list1, button_list2, button_list3])
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text,
                                    parse_mode="MarkdownV2", reply_markup=reply_markup, disable_web_page_preview=True)

    elif call.data == "gold":
        await bot.answer_callback_query(call.id)
        text = ("🟡 Gold:\n\n"
                "🎯 Track up to 150 wallets\n"
                "⚙️ Full Notification Customisation\n"
                "🔎 Contract safe scan\n"
                "💎 Access to our Premium Wallet and Contact Analysis channel\n"
                "💰 Find Alpha wallets and traders with Premium access\n\n"
                "**Payment Method: USDC | USDT | ETH**\n\n")
        text = escape(text, flag=0)

        ether_usdt_price = await get_eth_price()

        button_list0 = [
            types.InlineKeyboardButton(f"1 Month | {round(price_packages_usdt_usdc[10] / ether_usdt_price, 2)} ETH", callback_data=f"pay_sub_10_gold_{round(price_packages_usdt_usdc[10] / ether_usdt_price, 4)}"),
        ]
        button_list1 = [
            types.InlineKeyboardButton(f"3 Months | {round(price_packages_usdt_usdc[11] / ether_usdt_price, 2)} ETH", callback_data=f"pay_sub_11_gold_{round(price_packages_usdt_usdc[11] / ether_usdt_price, 4)}"),
        ]
        button_list2 = [
            types.InlineKeyboardButton(f"12 Months | {round(price_packages_usdt_usdc[12] / ether_usdt_price, 2)} ETH", callback_data=f"pay_sub_12_gold_{round(price_packages_usdt_usdc[12] / ether_usdt_price, 4)}"),
        ]
        button_list3 = [
            types.InlineKeyboardButton("⬅️ Back", callback_data="subscribe_menu"),
        ]
        reply_markup = types.InlineKeyboardMarkup([button_list0, button_list1, button_list2, button_list3])
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text,
                                    parse_mode="MarkdownV2", reply_markup=reply_markup, disable_web_page_preview=True)


    elif call.data.startswith("pay_sub_"):
        await bot.answer_callback_query(call.id)
        sub_type = int(call.data.split("_")[2])
        sub_tier = call.data.split("_")[3]
        # eth_value = await get_eth_value_from_usd(usd)
        eth_value = float(call.data.split("_")[4])
        if sub_type == 1:
            usd = price_packages_usdt_usdc[1]
            sub_period = "1 month"
        elif sub_type == 2:
            usd = price_packages_usdt_usdc[2]
            sub_period = "3 months"
        elif sub_type == 3:
            usd = price_packages_usdt_usdc[3]
            sub_period = "12 months"
        elif sub_type == 4:
            usd = price_packages_usdt_usdc[4]
            sub_period = "1 month"
        elif sub_type == 5:
            usd = price_packages_usdt_usdc[5]
            sub_period = "3 months"
        elif sub_type == 6:
            usd = price_packages_usdt_usdc[6]
            sub_period = "12 months"
        elif sub_type == 7:
            usd = price_packages_usdt_usdc[7]
            sub_period = "1 month"
        elif sub_type == 8:
            usd = price_packages_usdt_usdc[8]
            sub_period = "3 months"
        elif sub_type == 9:
            usd = price_packages_usdt_usdc[9]
            sub_period = "12 months"
        elif sub_type == 10:
            usd = price_packages_usdt_usdc[10]
            sub_period = "1 month"
        elif sub_type == 11:
            usd = price_packages_usdt_usdc[11]
            sub_period = "3 months"
        elif sub_type == 12:
            usd = price_packages_usdt_usdc[12]
            sub_period = "12 months"
        text = (f"You have chosen the **{sub_tier.upper()}** subscription.\n"
                f"For a period of {sub_period}.\n"
                "To pay:\n"
                f"`{eth_value}` ETH\n"
                "OR\n"
                f"`{usd}` USDT/USDC\n\n"
                f"Wallet: `{owner_wallet}`\n\n"
                "⚠️ Send only via the Ethereum network (ERC20).")
        text = escape(text, flag=0)

        button_list0 = [
            types.InlineKeyboardButton("#️⃣ Insert Transaction Hash #️⃣", callback_data=f"transaction_hash_{sub_tier}"),
        ]
        button_list1 = [
            types.InlineKeyboardButton("⬅️ Back", callback_data=f"{sub_tier}"),
        ]
        reply_markup = types.InlineKeyboardMarkup([button_list0, button_list1])

        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, parse_mode="MarkdownV2", reply_markup=reply_markup, disable_web_page_preview=True)

    elif call.data.startswith("transaction_hash"):
        await bot.answer_callback_query(call.id)
        sub_tier = call.data.split("_")[2]
        text = ("**Send the transaction hash to the chat.**\n"
                "**It is IMPORTANT that the transaction is confirmed.**")
        button_list1 = [
            types.InlineKeyboardButton("⬅️ Back", callback_data=f"{sub_tier}"),
        ]
        reply_markup = types.InlineKeyboardMarkup([button_list1])
        text = escape(text, flag=0)
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, parse_mode="MarkdownV2", reply_markup=reply_markup, disable_web_page_preview=True)


    elif call.data == "free_channel":
        await bot.answer_callback_query(call.id)
        text = ("⚡️ Hedex - Open To All ⚡️\n\n"
                "🎯 [Hedex Tracker](https://t.me/HedexTrackerBot) - Track upto 10 wallets.\n"
                "🔎 [Lite Channel](https://t.me/HedexLite) - Access to view top performing tokens + the best traders!\n\n"
                "We wanted to open the doors to everyone!")
        text = escape(text, flag=0)

        button_list1 = [
            types.InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="back_to_main_menu"),
            types.InlineKeyboardButton("Chat 💬", url="https://t.me/hedexbotgateway"),
        ]
        reply_markup = types.InlineKeyboardMarkup([button_list1])

        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, parse_mode="MarkdownV2", reply_markup=reply_markup, disable_web_page_preview=True)
    elif call.data == "information":
        await bot.answer_callback_query(call.id)
        text = ("⚡️Hedex Information & Guides! ⚡️\n\n"
                "Here you can find links to our **[Information channel](https://t.me/hedexbotinfo)** in the channel you’ll find our Guides, How To Use Hedex and How to read the data provided.\n\n"
                "If you are looking for something more specific then try the options below:👇\n\n"
                "**[Hedex Analysis Bot:](https://t.me/hedexbotinfo/4)**\n"
                "-[Commands](https://t.me/hedexbotinfo/4)\n"
                "-[Contract Scanner](https://t.me/hedexbotinfo/5)\n"
                "-[Wallet Deep Dive Scan](https://t.me/hedexbotinfo/6)\n"
                "-[Top Performers](https://t.me/hedexbotinfo/10)\n"
                "**~•~**\n"
                "**[Hedex Wallet Tracker:](https://t.me/hedexbotinfo/18)**\n"
                "-[Menus](https://t.me/hedexbotinfo/21)\n"
                "-[Configuration](https://t.me/hedexbotinfo/23)\n"
                "   + [Wallets Trigger](https://t.me/hedexbotinfo/24)\n"
                "   + [Time Trigger](https://t.me/hedexbotinfo/25)\n"
                "-[Adding Wallets](https://t.me/hedexbotinfo/26)\n"
                "-[Notifications](https://t.me/hedexbotinfo/32)\n"
                "-[Contact Scanner](https://t.me/hedexbotinfo/32)\n"
                "**~•~**\n"
                "**[Hedex Subscriptions](https://t.me/hedexbotinfo/17)**\n"
                "**~•~**\n"
                "[Questions & Answers](https://t.me/hedexbotinfo/16)\n"
                "**~•~**")
        text = escape(text, flag=0)

        button_list1 = [
            types.InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="back_to_main_menu"),
            types.InlineKeyboardButton("Chat 💬", url="https://t.me/hedexbotgateway"),
        ]
        reply_markup = types.InlineKeyboardMarkup([button_list1])

        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, parse_mode="MarkdownV2", reply_markup=reply_markup, disable_web_page_preview=True)

    elif call.data == "back_to_main_menu":
        await bot.answer_callback_query(call.id)
        text = ("⚡️ Welcome to Hedex! ⚡️\n"
                "This is our Portal bot which will navigate you around the Hedex ecosystem!\n\n"
                "Hedex has been built to help traders to find and track alpha wallets, help our users become more profitable and make them more consistent traders!\n\n"
                "⁉️ What does Hedex offer?\n"
                "💎Deep wallet analysis on contracts and Ethereum wallets to give you the best Alpha Traders.\n"
                "⚙️Track wallets with full user customisation.\n"
                "🔎 Scan contracts to keep you safe!\n\n"
                "Our Socials:\n"
                "[Website](https://www.hedexbot.com) | [YouTube](https://youtube.com/@Hedexbot?si=veDXXwp2jtjaHH6o) | [Twitter (X)](https://x.com/hedexbot?s=21&t=4O7fqwfoOCUDViGWXA1J0w)")
        text = escape(text, flag=0)
        button_list1 = [
            types.InlineKeyboardButton("Subscribe 💠", callback_data="subscribe_menu"),
            types.InlineKeyboardButton("Free 🆓", callback_data="free_channel"),
        ]
        button_list2 = [
            types.InlineKeyboardButton("Information ℹ️", callback_data="information"),
            types.InlineKeyboardButton("Chat 💬", url="https://t.me/hedexbotgateway"),
        ]

        reply_markup = types.InlineKeyboardMarkup([button_list1, button_list2])

        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, parse_mode="MarkdownV2", reply_markup=reply_markup, disable_web_page_preview=True)



@bot.message_handler(func=lambda message: True)
async def handle_message(message):
    chat_type = message.chat.type
    if chat_type == 'private':
        possible_txs_hash = message.text
        username = message.from_user.username
        user_id = message.from_user.id
        if possible_txs_hash[:2] == "0x":
            list_of_hash = get_hash_list()

            if possible_txs_hash not in list_of_hash:
                txs_status, paid_package = await check_transaction_hash(possible_txs_hash)
                if txs_status == True:
                    # premium
                    if paid_package == 1:
                        days_to_add = 30
                        current_date = datetime.datetime.now()
                        new_date = current_date + datetime.timedelta(days=days_to_add)
                        change_users_rights(username, 0, new_date, 1)

                        current_unix_time = int(time.time())
                        unix_time_plus_24_hours = current_unix_time + 86400

                        invite_link = await bot.create_chat_invite_link(private_group_id, expire_date=unix_time_plus_24_hours, member_limit=1)
                        invite_link = invite_link.invite_link
                        invite_link_to_prem_group_chat = await bot.create_chat_invite_link(premium_chat_group_id, expire_date=unix_time_plus_24_hours, member_limit=1)
                        invite_link_to_group_chat = invite_link_to_prem_group_chat.invite_link
                        text = escape(f"🎉 **Congratulations** 🎉\n**You have successfully purchased a PREMIUM subscription for 30 days!**\nPremium Channel: {invite_link}", flag=0)

                        txs_hash_append_in_bd(possible_txs_hash, message.chat.id, invite_link_to_group_chat, invite_link)

                        await bot.send_message(chat_id=message.chat.id, text=text, parse_mode="MarkdownV2")
                        await bot.send_message(chat_id=5614137400, text=f"⭐️New Customer⭐️\n\nUser: {username}\nPaid amount (equivalent): ≈ {price_packages_usdt_usdc[1]} USD\nPaid subscription: PREMIUM subscription.\nSubscription duration: 1 month")
                    elif paid_package == 2:
                        days_to_add = 90
                        current_date = datetime.datetime.now()
                        new_date = current_date + datetime.timedelta(days=days_to_add)
                        change_users_rights(username, 0, new_date, 1)

                        current_unix_time = int(time.time())
                        unix_time_plus_24_hours = current_unix_time + 86400

                        invite_link = await bot.create_chat_invite_link(private_group_id, expire_date=unix_time_plus_24_hours, member_limit=1)
                        invite_link = invite_link.invite_link
                        invite_link_to_prem_group_chat = await bot.create_chat_invite_link(premium_chat_group_id, expire_date=unix_time_plus_24_hours, member_limit=1)
                        invite_link_to_group_chat = invite_link_to_prem_group_chat.invite_link
                        text = escape(f"🎉 **Congratulations** 🎉\n**You have successfully purchased a PREMIUM subscription for 3 months!**\nPremium Channel: {invite_link}", flag=0)

                        txs_hash_append_in_bd(possible_txs_hash, message.chat.id, invite_link_to_group_chat, invite_link)

                        await bot.send_message(chat_id=message.chat.id, text=text, parse_mode="MarkdownV2")
                        await bot.send_message(chat_id=5614137400, text=f"⭐️New Customer⭐️\n\nUser: {username}\nPaid amount (equivalent): ≈ {price_packages_usdt_usdc[2]} USD\nPaid subscription: PREMIUM subscription.\nSubscription duration: 3 months")
                    elif paid_package == 3:
                        days_to_add = 365
                        current_date = datetime.datetime.now()
                        new_date = current_date + datetime.timedelta(days=days_to_add)
                        change_users_rights(username, 0, new_date, 1)

                        current_unix_time = int(time.time())
                        unix_time_plus_24_hours = current_unix_time + 86400

                        invite_link = await bot.create_chat_invite_link(private_group_id, expire_date=unix_time_plus_24_hours, member_limit=1)
                        invite_link = invite_link.invite_link
                        invite_link_to_prem_group_chat = await bot.create_chat_invite_link(premium_chat_group_id, expire_date=unix_time_plus_24_hours, member_limit=1)
                        invite_link_to_group_chat = invite_link_to_prem_group_chat.invite_link
                        text = escape(f"🎉 **Congratulations** 🎉\n**You have successfully purchased a PREMIUM subscription for 12 months!**\nPremium Channel: {invite_link}\n", flag=0)

                        txs_hash_append_in_bd(possible_txs_hash, message.chat.id, invite_link_to_group_chat, invite_link)

                        await bot.send_message(chat_id=message.chat.id, text=text, parse_mode="MarkdownV2")
                        await bot.send_message(chat_id=5614137400, text=f"⭐️New Customer⭐️\n\nUser: {username}\nPaid amount (equivalent): ≈ {price_packages_usdt_usdc[3]} USD\nPaid subscription: PREMIUM subscription.\nSubscription duration: 12 months")
                    # bronze
                    elif paid_package == 4:
                        days_to_add = 30
                        current_date = datetime.datetime.now()
                        new_date = current_date + datetime.timedelta(days=days_to_add)
                        change_users_rights(username, 0, new_date, 1)

                        current_unix_time = int(time.time())
                        unix_time_plus_24_hours = current_unix_time + 86400

                        invite_link = await bot.create_chat_invite_link(private_group_id, expire_date=unix_time_plus_24_hours, member_limit=1)
                        invite_link = invite_link.invite_link
                        invite_link_to_prem_group_chat = await bot.create_chat_invite_link(premium_chat_group_id, expire_date=unix_time_plus_24_hours, member_limit=1)
                        invite_link_to_group_chat = invite_link_to_prem_group_chat.invite_link
                        text = escape(f"🎉 **Congratulations** 🎉\n**You have successfully purchased a BRONZE subscription for 30 days!**\nPremium Channel: {invite_link}\nWallet Tracker Bot: @HedexTrackerBot", flag=0)

                        txs_hash_append_in_bd(possible_txs_hash, message.chat.id, invite_link_to_group_chat, invite_link)
                        await change_wallet_track_limit(30, user_id)

                        await bot.send_message(chat_id=message.chat.id, text=text, parse_mode="MarkdownV2")
                        await bot.send_message(chat_id=5614137400, text=f"⭐️New Customer⭐️\n\nUser: {username}\nPaid amount (equivalent): ≈ {price_packages_usdt_usdc[4]} USD\nPaid subscription: BRONZE subscription.\nSubscription duration: 1 month")
                    elif paid_package == 5:
                        days_to_add = 90
                        current_date = datetime.datetime.now()
                        new_date = current_date + datetime.timedelta(days=days_to_add)
                        change_users_rights(username, 0, new_date, 1)

                        current_unix_time = int(time.time())
                        unix_time_plus_24_hours = current_unix_time + 86400

                        invite_link = await bot.create_chat_invite_link(private_group_id, expire_date=unix_time_plus_24_hours, member_limit=1)
                        invite_link = invite_link.invite_link
                        invite_link_to_prem_group_chat = await bot.create_chat_invite_link(premium_chat_group_id, expire_date=unix_time_plus_24_hours, member_limit=1)
                        invite_link_to_group_chat = invite_link_to_prem_group_chat.invite_link
                        text = escape(f"🎉 **Congratulations** 🎉\n**You have successfully purchased a BRONZE subscription for 3 months!**\nPremium Channel: {invite_link}\nWallet Tracker Bot: @HedexTrackerBot", flag=0)

                        txs_hash_append_in_bd(possible_txs_hash, message.chat.id, invite_link_to_group_chat, invite_link)
                        await change_wallet_track_limit(30, user_id)

                        await bot.send_message(chat_id=message.chat.id, text=text, parse_mode="MarkdownV2")
                        await bot.send_message(chat_id=5614137400, text=f"⭐️New Customer⭐️\n\nUser: {username}\nPaid amount (equivalent): ≈ {price_packages_usdt_usdc[5]} USD\nPaid subscription: BRONZE subscription.\nSubscription duration: 3 months")
                    elif paid_package == 6:
                        days_to_add = 365
                        current_date = datetime.datetime.now()
                        new_date = current_date + datetime.timedelta(days=days_to_add)
                        change_users_rights(username, 0, new_date, 1)

                        current_unix_time = int(time.time())
                        unix_time_plus_24_hours = current_unix_time + 86400

                        invite_link = await bot.create_chat_invite_link(private_group_id, expire_date=unix_time_plus_24_hours, member_limit=1)
                        invite_link = invite_link.invite_link
                        invite_link_to_prem_group_chat = await bot.create_chat_invite_link(premium_chat_group_id, expire_date=unix_time_plus_24_hours, member_limit=1)
                        invite_link_to_group_chat = invite_link_to_prem_group_chat.invite_link
                        text = escape(f"🎉 **Congratulations** 🎉\n**You have successfully purchased a BRONZE subscription for 12 months!**\nPremium Channel: {invite_link}\nWallet Tracker Bot: @HedexTrackerBot", flag=0)

                        txs_hash_append_in_bd(possible_txs_hash, message.chat.id, invite_link_to_group_chat, invite_link)
                        await change_wallet_track_limit(30, user_id)

                        await bot.send_message(chat_id=message.chat.id, text=text, parse_mode="MarkdownV2")
                        await bot.send_message(chat_id=5614137400, text=f"⭐️New Customer⭐️\n\nUser: {username}\nPaid amount (equivalent): ≈ {price_packages_usdt_usdc[6]} USD\nPaid subscription: BRONZE subscription.\nSubscription duration: 12 months")
                    # silver
                    if paid_package == 7:
                        days_to_add = 30
                        current_date = datetime.datetime.now()
                        new_date = current_date + datetime.timedelta(days=days_to_add)
                        change_users_rights(username, 1, new_date, 1)

                        current_unix_time = int(time.time())
                        unix_time_plus_24_hours = current_unix_time + 86400

                        invite_link = await bot.create_chat_invite_link(private_group_id, expire_date=unix_time_plus_24_hours, member_limit=1)
                        invite_link = invite_link.invite_link
                        invite_link_to_prem_group_chat = await bot.create_chat_invite_link(premium_chat_group_id, expire_date=unix_time_plus_24_hours, member_limit=1)
                        invite_link_to_group_chat = invite_link_to_prem_group_chat.invite_link
                        text = escape(f"🎉 **Congratulations** 🎉\n**You have successfully purchased a SILVER subscription for 30 days!**\nPremium Channel: {invite_link}\nWallet Tracker Bot: @HedexTrackerBot", flag=0)

                        txs_hash_append_in_bd(possible_txs_hash, message.chat.id, invite_link_to_group_chat, invite_link)
                        await change_wallet_track_limit(70, user_id)

                        await bot.send_message(chat_id=message.chat.id, text=text, parse_mode="MarkdownV2")
                        await bot.send_message(chat_id=5614137400, text=f"⭐️New Customer⭐️\n\nUser: {username}\nPaid amount (equivalent): ≈ {price_packages_usdt_usdc[7]} USD\nPaid subscription: SILVER subscription.\nSubscription duration: 1 month")
                    elif paid_package == 8:
                        days_to_add = 90
                        current_date = datetime.datetime.now()
                        new_date = current_date + datetime.timedelta(days=days_to_add)
                        change_users_rights(username, 1, new_date, 1)

                        current_unix_time = int(time.time())
                        unix_time_plus_24_hours = current_unix_time + 86400

                        invite_link = await bot.create_chat_invite_link(private_group_id, expire_date=unix_time_plus_24_hours, member_limit=1)
                        invite_link = invite_link.invite_link
                        invite_link_to_prem_group_chat = await bot.create_chat_invite_link(premium_chat_group_id, expire_date=unix_time_plus_24_hours, member_limit=1)
                        invite_link_to_group_chat = invite_link_to_prem_group_chat.invite_link
                        text = escape(f"🎉 **Congratulations** 🎉\n**You have successfully purchased a SILVER subscription for 3 months!**\nPremium Channel: {invite_link}\nWallet Tracker Bot: @HedexTrackerBot", flag=0)

                        txs_hash_append_in_bd(possible_txs_hash, message.chat.id, invite_link_to_group_chat, invite_link)
                        await change_wallet_track_limit(70, user_id)

                        await bot.send_message(chat_id=message.chat.id, text=text, parse_mode="MarkdownV2")
                        await bot.send_message(chat_id=5614137400, text=f"⭐️New Customer⭐️\n\nUser: {username}\nPaid amount (equivalent): ≈ {price_packages_usdt_usdc[8]} USD\nPaid subscription: SILVER subscription.\nSubscription duration: 3 months")
                    elif paid_package == 9:
                        days_to_add = 365
                        current_date = datetime.datetime.now()
                        new_date = current_date + datetime.timedelta(days=days_to_add)
                        change_users_rights(username, 1, new_date, 1)

                        current_unix_time = int(time.time())
                        unix_time_plus_24_hours = current_unix_time + 86400

                        invite_link = await bot.create_chat_invite_link(private_group_id, expire_date=unix_time_plus_24_hours, member_limit=1)
                        invite_link = invite_link.invite_link
                        invite_link_to_prem_group_chat = await bot.create_chat_invite_link(premium_chat_group_id, expire_date=unix_time_plus_24_hours, member_limit=1)
                        invite_link_to_group_chat = invite_link_to_prem_group_chat.invite_link
                        text = escape(f"🎉 **Congratulations** 🎉\n**You have successfully purchased a SILVER subscription for 12 months!**\nPremium Channel: {invite_link}\nWallet Tracker Bot: @HedexTrackerBot", flag=0)

                        txs_hash_append_in_bd(possible_txs_hash, message.chat.id, invite_link_to_group_chat, invite_link)
                        await change_wallet_track_limit(70, user_id)

                        await bot.send_message(chat_id=message.chat.id, text=text, parse_mode="MarkdownV2")
                        await bot.send_message(chat_id=5614137400, text=f"⭐️New Customer⭐️\n\nUser: {username}\nPaid amount (equivalent): ≈ {price_packages_usdt_usdc[9]} USD\nPaid subscription: SILVER subscription.\nSubscription duration: 12 months")
                    # gold
                    if paid_package == 10:
                        days_to_add = 30
                        current_date = datetime.datetime.now()
                        new_date = current_date + datetime.timedelta(days=days_to_add)
                        change_users_rights(username, 1, new_date, 1)

                        current_unix_time = int(time.time())
                        unix_time_plus_24_hours = current_unix_time + 86400

                        invite_link = await bot.create_chat_invite_link(private_group_id, expire_date=unix_time_plus_24_hours, member_limit=1)
                        invite_link = invite_link.invite_link
                        invite_link_to_prem_group_chat = await bot.create_chat_invite_link(premium_chat_group_id, expire_date=unix_time_plus_24_hours, member_limit=1)
                        invite_link_to_group_chat = invite_link_to_prem_group_chat.invite_link
                        text = escape(f"🎉 **Congratulations** 🎉\n**You have successfully purchased a GOLD subscription for 30 days!**\nPremium Channel: {invite_link}\nWallet Tracker Bot: @HedexTrackerBot", flag=0)

                        txs_hash_append_in_bd(possible_txs_hash, message.chat.id, invite_link_to_group_chat, invite_link)
                        await change_wallet_track_limit(150, user_id)

                        await bot.send_message(chat_id=message.chat.id, text=text, parse_mode="MarkdownV2")
                        await bot.send_message(chat_id=5614137400, text=f"⭐️New Customer⭐️\n\nUser: {username}\nPaid amount (equivalent): ≈ {price_packages_usdt_usdc[10]} USD\nPaid subscription: GOLD subscription.\nSubscription duration: 1 month")
                    elif paid_package == 11:
                        days_to_add = 90
                        current_date = datetime.datetime.now()
                        new_date = current_date + datetime.timedelta(days=days_to_add)
                        change_users_rights(username, 1, new_date, 1)

                        current_unix_time = int(time.time())
                        unix_time_plus_24_hours = current_unix_time + 86400

                        invite_link = await bot.create_chat_invite_link(private_group_id, expire_date=unix_time_plus_24_hours, member_limit=1)
                        invite_link = invite_link.invite_link
                        invite_link_to_prem_group_chat = await bot.create_chat_invite_link(premium_chat_group_id, expire_date=unix_time_plus_24_hours, member_limit=1)
                        invite_link_to_group_chat = invite_link_to_prem_group_chat.invite_link
                        text = escape(f"🎉 **Congratulations** 🎉\n**You have successfully purchased a GOLD subscription for 3 months!**\nPremium Channel: {invite_link}\nWallet Tracker Bot: @HedexTrackerBot", flag=0)

                        txs_hash_append_in_bd(possible_txs_hash, message.chat.id, invite_link_to_group_chat, invite_link)
                        await change_wallet_track_limit(150, user_id)

                        await bot.send_message(chat_id=message.chat.id, text=text, parse_mode="MarkdownV2")
                        await bot.send_message(chat_id=5614137400, text=f"⭐️New Customer⭐️\n\nUser: {username}\nPaid amount (equivalent): ≈ {price_packages_usdt_usdc[11]} USD\nPaid subscription: GOLD subscription.\nSubscription duration: 3 months")
                    elif paid_package == 12:
                        days_to_add = 365
                        current_date = datetime.datetime.now()
                        new_date = current_date + datetime.timedelta(days=days_to_add)
                        change_users_rights(username, 1, new_date, 1)

                        current_unix_time = int(time.time())
                        unix_time_plus_24_hours = current_unix_time + 86400

                        invite_link = await bot.create_chat_invite_link(private_group_id, expire_date=unix_time_plus_24_hours, member_limit=1)
                        invite_link = invite_link.invite_link
                        invite_link_to_prem_group_chat = await bot.create_chat_invite_link(premium_chat_group_id, expire_date=unix_time_plus_24_hours, member_limit=1)
                        invite_link_to_group_chat = invite_link_to_prem_group_chat.invite_link
                        text = escape(f"🎉 **Congratulations** 🎉\n**You have successfully purchased a GOLD subscription for 12 months!**\nPremium Channel: {invite_link}\nWallet Tracker Bot: @HedexTrackerBot", flag=0)

                        txs_hash_append_in_bd(possible_txs_hash, message.chat.id, invite_link_to_group_chat, invite_link)
                        await change_wallet_track_limit(150, user_id)

                        await bot.send_message(chat_id=message.chat.id, text=text, parse_mode="MarkdownV2")
                        await bot.send_message(chat_id=5614137400, text=f"⭐️New Customer⭐️\n\nUser: {username}\nPaid amount (equivalent): ≈ {price_packages_usdt_usdc[12]} USD\nPaid subscription: GOLD subscription.\nSubscription duration: 12 months")
                else:
                    await bot.send_message(chat_id=message.chat.id, text="⛔️*This is an incorrect transaction\, please send another one\.*", parse_mode="MarkdownV2")
            else:
                await bot.send_message(chat_id=message.chat.id, text="⛔️*This is an incorrect transaction\, please send another one\.*", parse_mode="MarkdownV2")


async def main():
    bot_task = asyncio.create_task(bot.polling(non_stop=True, request_timeout=120))
    await asyncio.gather(bot_task)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()
