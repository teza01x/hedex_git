import asyncio
from bs4 import BeautifulSoup
from config import *
from asc_cloud import *
from sql_scripts import *


async def clean_text(text):
    split_terms = ["Represents", "Shows", "Presents", "Indicates"]
    for term in split_terms:
        if term in text:
            return text.split(term)[0].strip()
    return text


async def first_point(html, wallet_address):
    try:
        soup = BeautifulSoup(html, 'html.parser')

        header = list()
        body = list()
        index = 0

        labels = [
            "PNL:",
            "Trading Volume(90D) :",
            "Total Trades(90D) :",
            "Balance:"
        ]

        for label in labels:
            element = soup.select_one(f'p:-soup-contains("{label}")')
            if element:
                value = element.get_text(strip=True).replace(label, '')
                cleaned_value = await clean_text(value)
                header.append(f"**{label}** {cleaned_value}")


        trade_elements = soup.select('.table-row__desktop_grid a[href^="/app/eth/chart/"]')

        if len(trade_elements) > 3:
            for trade_element in trade_elements[:3]:
                trade_name = trade_element.select_one('p.text-white').get_text()
                try:
                    try:
                        trade_value = trade_element.find_next('p', class_='self-center text-center text-[#16c784] font-extrabold').get_text()
                    except:
                        try:
                            trade_value = trade_element.find_next('p', class_='self-center text-center text-[#16c784] font-bold').get_text()
                        except:
                            trade_value = trade_element.find_next('p', class_='self-center text-center text-[#16c784] font-semibold').get_text()
                except:
                    trade_value = trade_element.find_next('p', class_='self-center text-center text-[#16c784]').get_text()
                trade_percentage = trade_element.find_next('p', class_='self-center text-center text-white').get_text()
                body.append(f"**{trade_name}:** {trade_value} - {trade_percentage}")
        else:
            for trade_element in trade_elements:
                trade_name = trade_element.select_one('p.text-white').get_text()
                try:
                    try:
                        trade_value = trade_element.find_next('p', class_='self-center text-center text-[#16c784] font-extrabold').get_text()
                    except:
                        try:
                            trade_value = trade_element.find_next('p', class_='self-center text-center text-[#16c784] font-bold').get_text()
                        except:
                            trade_value = trade_element.find_next('p', class_='self-center text-center text-[#16c784] font-semibold').get_text()
                except:
                    trade_value = trade_element.find_next('p', class_='self-center text-center text-[#16c784]').get_text()
                trade_percentage = trade_element.find_next('p', class_='self-center text-center text-white').get_text()
                body.append(f"**{trade_name}:** {trade_value} - {trade_percentage}")


        # risk calculation
        for label in labels:
            element = soup.select_one(f'p:-soup-contains("{label}")')
            if element:
                value = element.get_text(strip=True).replace(label, '')
                cleaned_value = await clean_text(value)
                if label == "PNL:":
                    pnl_value = float(cleaned_value[1:].replace(",", ''))
                elif label == "Trading Volume(90D) :":
                    trading_volume_value = float(cleaned_value[1:].replace(",", ''))


        pnl_percentage = (pnl_value / trading_volume_value) * 100

        if pnl_percentage > 40:
            risk = "🟢"
            top_wallets_list = check_top_list_wallets()
            if wallet_address not in top_wallets_list:
                add_new_wallet_in_top_list(wallet_address, pnl_value)
        elif 20 <= pnl_percentage <= 39:
            risk = "🟠"
        else:
            risk = "🔴"

        if pnl_value < 0:
            risk = "💩"

        new_header = list()
        for point in header:
            index += 1
            if index == 1:
                new_header.append("💰" + point)
            elif index == 2:
                new_header.append("📊" + point)
            elif index == 3:
                new_header.append("#️⃣" + point)

        index = 0
        new_body = list()
        for point in body:
            index += 1
            if index == 1:
                new_body.append("🥇" + point)
            elif index == 2:
                new_body.append("🥈" + point)
            elif index == 3:
                new_body.append("🥉" + point)

        while True:
            first_point_info_wallet_age = await first_pass_cycle_part2(wallet_address)
            if first_point_info_wallet_age == "busy":
                await asyncio.sleep(5)
            elif first_point_info_wallet_age[0] == "free":
                ethscan_html = first_point_info_wallet_age[1]
                break

        wallet_age = await first_point_part2(ethscan_html)
        trade_router = await first_point_part3(ethscan_html)

        if "Banana Gun 🍌🔫 : ❌" in trade_router and (risk == "🟠" or risk == "🟢"):
            top_daily_wallets_list = check_top_daily_list_wallets()
            if wallet_address not in top_daily_wallets_list:
                add_new_wallet_in_top_daily_list_nobanana(wallet_address, pnl_value)
            top_weekly_wallets_list = check_top_weekly_list_wallets()
            if wallet_address not in top_weekly_wallets_list:
                add_new_wallet_in_top_weekly_list_nobanana(wallet_address, pnl_value)

        scanned_before = wallet_count_of_contracts(wallet_address.lower())
        if scanned_before == 1:
            scanned_before_str = "{} time".format(scanned_before)
        else:
            scanned_before_str = "{} times".format(scanned_before)

        scanned_contr_coin_list = list()
        if scanned_before > 0:
            scanned_contracts = [i for i in scanned_coins_and_contracts(wallet_address.lower())]
            for count_contract in range(len(scanned_contracts)):
                scanned_contract_result = scanned_contracts[count_contract][0]
                scanned_coin_result = scanned_contracts[count_contract][1]
                if count_contract == 0:
                    scanned_contr_coin_list.append("1️⃣ `${}` 📈 [Dexscreener](https://dexscreener.com/ethereum/{}) **|** [DexCheck](https://dexcheck.ai/app/eth/chart/{})".format(scanned_coin_result, scanned_contract_result, scanned_contract_result))
                elif count_contract == 1:
                    scanned_contr_coin_list.append("2️⃣ `${}` 📈 [Dexscreener](https://dexscreener.com/ethereum/{}) **|** [DexCheck](https://dexcheck.ai/app/eth/chart/{})".format(scanned_coin_result, scanned_contract_result, scanned_contract_result))
                elif count_contract == 2:
                    scanned_contr_coin_list.append("3️⃣ `${}` 📈 [Dexscreener](https://dexscreener.com/ethereum/{}) **|** [DexCheck](https://dexcheck.ai/app/eth/chart/{})".format(scanned_coin_result, scanned_contract_result, scanned_contract_result))
                elif count_contract == 3:
                    scanned_contr_coin_list.append("4️⃣ `${}` 📈 [Dexscreener](https://dexscreener.com/ethereum/{}) **|** [DexCheck](https://dexcheck.ai/app/eth/chart/{})".format(scanned_coin_result, scanned_contract_result, scanned_contract_result))
                elif count_contract == 4:
                    scanned_contr_coin_list.append("5️⃣ `${}` 📈 [Dexscreener](https://dexscreener.com/ethereum/{}) **|** [DexCheck](https://dexcheck.ai/app/eth/chart/{})".format(scanned_coin_result, scanned_contract_result, scanned_contract_result))
                elif count_contract == 5:
                    scanned_contr_coin_list.append("6️⃣ `${}` 📈 [Dexscreener](https://dexscreener.com/ethereum/{}) **|** [DexCheck](https://dexcheck.ai/app/eth/chart/{})".format(scanned_coin_result, scanned_contract_result, scanned_contract_result))
                elif count_contract == 6:
                    scanned_contr_coin_list.append("7️⃣ `${}` 📈 [Dexscreener](https://dexscreener.com/ethereum/{}) **|** [DexCheck](https://dexcheck.ai/app/eth/chart/{})".format(scanned_coin_result, scanned_contract_result, scanned_contract_result))
                elif count_contract == 7:
                    scanned_contr_coin_list.append("8️⃣ `${}` 📈 [Dexscreener](https://dexscreener.com/ethereum/{}) **|** [DexCheck](https://dexcheck.ai/app/eth/chart/{})".format(scanned_coin_result, scanned_contract_result, scanned_contract_result))
                elif count_contract == 8:
                    scanned_contr_coin_list.append("9️⃣ `${}` 📈 [Dexscreener](https://dexscreener.com/ethereum/{}) **|** [DexCheck](https://dexcheck.ai/app/eth/chart/{})".format(scanned_coin_result, scanned_contract_result, scanned_contract_result))
                elif count_contract == 9:
                    scanned_contr_coin_list.append("🔟 `${}` 📈 [Dexscreener](https://dexscreener.com/ethereum/{}) **|** [DexCheck](https://dexcheck.ai/app/eth/chart/{})".format(scanned_coin_result, scanned_contract_result, scanned_contract_result))
                else:
                    pass

        private_group = "**Wallet:** `{}`\n🔗 : [Etherscan](https://etherscan.io/address/{})\n\n{}\n**👶Wallet Age: {}**\n\n🔥**3 Highest Profit/ROI:**🔥\n{}\n\n{}\n\n⚠️ **Profitability:** {}\n**🔎 Scanned Before: ✅ |** {}\n{}\n".format(wallet_address, wallet_address, "\n".join(new_header), wallet_age, "\n".join(new_body), trade_router, risk, scanned_before_str, "\n".join(scanned_contr_coin_list))

        standard_group = "**Wallet:** [0x..(Upgrade to Premium to see full address)](https://t.me/HedexPortalBot)\n\n{}\n👶**Wallet Age: {}**\n\n🔥**3 Highest Profit/ROI:**🔥\n{}\n\n{}\n\n⚠️ **Profitability:** {}\n**🔎 Scanned Before: ✅ |** {}\n{}\n".format("\n".join(new_header), wallet_age, "\n".join(new_body), trade_router, risk, scanned_before_str, "\n".join(scanned_contr_coin_list))

        private_group = private_group + "\n⚡️ `Powered By Hedex` ⚡️\n🤖 @HedexPortalBot 🤖"
        standard_group = standard_group + "\n⚡️ `Powered By Hedex` ⚡️\n🤖 @HedexPortalBot 🤖"

        return private_group, standard_group
    except Exception as error:
        print(error)


async def first_point_part2(html):
    soup = BeautifulSoup(html, 'html.parser')

    last_txn_sent = soup.find(text="First Txn Sent")
    if last_txn_sent:
        last_txn_info = last_txn_sent.find_next().text

        wallet_age = last_txn_info.split(" ")
        return " ".join(wallet_age[2:-1])
    return "Unknown"


async def first_point_part3(html):
    soup = BeautifulSoup(html, 'html.parser')

    list_of_transactions = soup.find("div", class_="tab-pane fade show active")
    routers = soup.find_all("div", class_="d-flex align-items-center gap-1")

    trade_routers = list()

    for route in routers:
        trade_router = route.text
        if "Maestro" in trade_router and "Maestro" not in trade_routers:
            trade_routers.append("Maestro")
        elif "Banana" in trade_router and "Banana" not in trade_routers:
            trade_routers.append("Banana")
        elif "Unibot" in trade_router and "Unibot" not in trade_routers:
            trade_routers.append("Unibot")

    result = "🤖 **Trade Router:**\nMaestro 🎩 : ❌\nBanana Gun 🍌🔫 : ❌\nUnibot 🦄 : ❌"
    for router in trade_routers:
        if router == "Maestro":
            result = result.replace("Maestro 🎩 : ❌", "Maestro 🎩 :✅")
        elif router == "Banana":
            result = result.replace("Banana Gun 🍌🔫 : ❌", "Banana Gun 🍌🔫 : ✅")
        elif router == "Unibot":
            result = result.replace("Unibot 🦄 : ❌", "Unibot 🦄 : ✅")

    return result


async def second_point(html, contract_address):
    soup = BeautifulSoup(html, 'html.parser')

    private_template = list()
    standard_template = list()

    coin_pair_element = soup.find('h2', class_='chakra-heading custom-hvdbl1')

    coin_pair = coin_pair_element.text
    coin_pair = coin_pair.replace("Copy token address", "")


    block_txns = soup.find('div', class_='custom-17mi4hx')

    txns = block_txns.find_all('div', class_='custom-kfd3si')

    index = 0
    for txn in txns:
        href = txn.find('a')['href']
        wallet = href.split('/')[-1]
        try:
            bought = txn.find('span', class_="chakra-text custom-rcecxm").get_text().strip()
            try:
                txs = txn.find_all('span', class_="chakra-text custom-13ppmr2")[0].get_text().strip()
                bought_txns = "({})".format(txs.split()[0].split('/')[-1] + " txns")
            except:
                bought_txns = ''
        except:
            bought = "N/A"
            bought_txns = ''

        try:
            sold = txn.find('span', class_="chakra-text custom-dv3t8y").get_text().strip()
        except:
            sold = "N/A"
        try:
            if bought == "N/A":
                try:
                    txs = txn.find_all('span', class_="chakra-text custom-13ppmr2")[0].get_text().strip()
                    sold_txns = "({})".format(txs.split()[0].split('/')[-1] + " txns")
                except:
                    sold_txns = ''
            else:
                txs = txn.find_all('span', class_="chakra-text custom-13ppmr2")[1].get_text().strip()
                sold_txns = "({})".format(txs.split()[0].split('/')[-1] + " txns")
        except:
            sold_txns = ''

        try:
            pnl = txn.find('div', class_="custom-1e9y0rl").get_text().strip()
        except:
            pnl = "N/A"

        try:
            unrealized = txn.find('div', class_="custom-1hd7h4r").get_text().strip()
            if unrealized == "-":
                unrealized = "N/A"
        except:
            unrealized = "N/A"

        try:
            balance_element = txn.find('div', class_="custom-1cicvqe").get_text().strip()
            balance = " of ".join(balance_element.split("of"))
        except:
            balance = "Unknown"


        if bought == "N/A" or sold == "N/A":
            pass
        else:
            check_bought = bought.replace("$", "").replace(",", ".").replace("<", "").replace(">", "")
            check_sold = sold.replace("$", "").replace(",", ".").replace("<", "").replace(">", "")

            if "K" in check_bought:
                check_bought = float(check_bought.replace("K", "")) * 1000
            elif "M" in check_bought:
                check_bought = float(check_bought.replace("M", "")) * 1000000
            else:
                check_bought = float(check_bought)
            if "K" in check_sold:
                check_sold = float(check_sold.replace("K", "")) * 1000
            elif "M" in check_sold:
                check_sold = float(check_sold.replace("M", "")) * 1000000
            else:
                check_sold = float(check_sold)


            difference = abs(check_bought - check_sold)
            threshold_20_percent = 0.2 * min(check_bought, check_sold)

            if difference > threshold_20_percent:
                index += 1
                if index == 1:
                    private_template.append(f"🥇**Wallet:** `{wallet}`\n🔗 : [Etherscan](https://etherscan.io/address/{wallet})\n\n🔥**Bought:** {bought} {bought_txns}\n❌**Sold:** {sold} {sold_txns}\n📊**PNL:** {pnl}\n🚀**Unrealized:** {unrealized}\n💰**Balance:** {balance}\n")
                    standard_template.append(f"🥇**Wallet:** [0x..(Upgrade to Premium)](https://t.me/HedexPortalBot)\n\n🔥**Bought:** {bought} {bought_txns}\n❌**Sold:** {sold} {sold_txns}\n📊**PNL:** {pnl}\n🚀**Unrealized:** {unrealized}\n💰**Balance:** {balance}\n")
                elif index == 2:
                    private_template.append(f"🥈**Wallet:** `{wallet}`\n🔗 : [Etherscan](https://etherscan.io/address/{wallet})\n\n🔥**Bought:** {bought} {bought_txns}\n❌**Sold:** {sold} {sold_txns}\n📊**PNL:** {pnl}\n🚀**Unrealized:** {unrealized}\n💰**Balance:** {balance}\n")
                    standard_template.append(f"🥈**Wallet:** [0x..(Upgrade to Premium)](https://t.me/HedexPortalBot)\n\n🔥**Bought:** {bought} {bought_txns}\n❌**Sold:** {sold} {sold_txns}\n📊**PNL:** {pnl}\n🚀**Unrealized:** {unrealized}\n💰**Balance:** {balance}\n")
                elif index == 3:
                    private_template.append(f"🥉**Wallet:** `{wallet}`\n🔗 : [Etherscan](https://etherscan.io/address/{wallet})\n\n🔥**Bought:** {bought} {bought_txns}\n❌**Sold:** {sold} {sold_txns}\n📊**PNL:** {pnl}\n🚀**Unrealized:** {unrealized}\n💰**Balance:** {balance}\n")
                    standard_template.append(f"🥉**Wallet:** [0x..(Upgrade to Premium)](https://t.me/HedexPortalBot)\n\n🔥**Bought:** {bought} {bought_txns}\n❌**Sold:** {sold} {sold_txns}\n📊**PNL:** {pnl}\n🚀**Unrealized:** {unrealized}\n💰**Balance:** {balance}\n")
                else:
                    private_template.append(f"**RANK #{index}**\n**Wallet:** `{wallet}`\n🔗 : [Etherscan](https://etherscan.io/address/{wallet})\n\n🔥**Bought:** {bought} {bought_txns}\n❌**Sold:** {sold} {sold_txns}\n📊**PNL:** {pnl}\n🚀**Unrealized:** {unrealized}\n💰**Balance:** {balance}\n")
                    standard_template.append(f"**RANK #{index}**\n**Wallet:** [0x..(Upgrade to Premium)](https://t.me/HedexPortalBot)\n\n🔥**Bought:** {bought} {bought_txns}\n❌**Sold:** {sold} {sold_txns}\n📊**PNL:** {pnl}\n🚀**Unrealized:** {unrealized}\n💰**Balance:** {balance}\n")
            else:
                pass


    private_group = f"`${coin_pair}`\n\n📄Contract:\n`{contract_address}`\n\n" + f"📈 Chart: [Dextools](https://www.dextools.io/app/en/ether/pair-explorer/{contract_address}) | [Dexscreener](https://dexscreener.com/ethereum/{contract_address})\n\n" + "\n".join(private_template[:5])
    standard_group = f"`${coin_pair}`\n\n📄Contract:\n`{contract_address}`\n\n" + f"📈 Chart: [Dextools](https://www.dextools.io/app/en/ether/pair-explorer/{contract_address}) | [Dexscreener](https://dexscreener.com/ethereum/{contract_address})\n\n" + "\n".join(standard_template[:5])

    private_group = private_group + "\n⚡️ `Powered By Hedex` ⚡️\n🤖 @HedexPortalBot 🤖"
    standard_group = standard_group + "\n⚡️ `Powered By Hedex` ⚡️\n🤖 @HedexPortalBot 🤖"

    return private_group, standard_group


async def third_point(html, iteration):
    soup = BeautifulSoup(html, 'html.parser')

    body = list()
    body_standard = list()
    hrefs = list()
    result = list()
    result_standard = list()
    contract_addresses = list()

    table_div = soup.find('div', class_='ds-dex-table ds-dex-table-top')
    a_elements = table_div.find_all('a', class_='ds-dex-table-row ds-dex-table-row-top')

    for a_element in a_elements[:5]:
        chain = a_element.find('img', class_='ds-dex-table-row-chain-icon')['title']
        pair = a_element.find('span', class_='ds-dex-table-row-base-token-symbol').get_text()
        pair += "/" + a_element.find('span', class_='ds-dex-table-row-quote-token-symbol').get_text()
        address = a_element['href'].split('/')[-1]


        daily_percentage_change = a_element.find_all('div', class_='ds-table-data-cell ds-dex-table-row-col-price-change')
        try:
            price_changes = daily_percentage_change[-1].find_all('span', class_='ds-change-perc ds-change-perc-pos')
            price_change = price_changes[-1].get_text()
            body.append(f"{pair} 📈 {price_change} - `{address}`\n" + f"📊 Chart: [Dextools](https://www.dextools.io/app/en/ether/pair-explorer/{address}) | [Dexscreener](https://dexscreener.com/ethereum/{address})\n")
            contract_addresses.append(address)
            body_standard.append(f"{pair} 📈 {price_change} - `{address}`\n" + f"📊 Chart: [Dextools](https://www.dextools.io/app/en/ether/pair-explorer/{address}) | [Dexscreener](https://dexscreener.com/ethereum/{address})\n")
            hrefs.append("https://dexscreener.com" + a_element['href'])
        except:
            price_changes = daily_percentage_change[-1].find_all('span', class_='ds-change-perc ds-change-perc-neg')
            price_change = price_changes[-1].get_text()
            body.append(f"{pair} 📉 {price_change} - `{address}`\n" + f"📊 Chart: [Dextools](https://www.dextools.io/app/en/ether/pair-explorer/{address}) | [Dexscreener](https://dexscreener.com/ethereum/{address})\n")
            contract_addresses.append(address)
            body_standard.append(f"{pair} 📉 {price_change} - `{address}`\n" + f"📊 Chart: [Dextools](https://www.dextools.io/app/en/ether/pair-explorer/{address}) | [Dexscreener](https://dexscreener.com/ethereum/{address})\n")
            hrefs.append("https://dexscreener.com" + a_element['href'])



    for index, item in enumerate(body, 1):
        if index == 1:
            result.append(f"🥇{item}")
        elif index == 2:
            result.append(f"🥈{item}")
        elif index == 3:
            result.append(f"🥉{item}")
        else:
            result.append(f"**{index})** {item}")

    for index, item in enumerate(body_standard, 1):
        if index == 1:
            result_standard.append(f"🥇{item}")
        elif index == 2:
            result_standard.append(f"🥈{item}")
        elif index == 3:
            result_standard.append(f"🥉{item}")
        else:
            result_standard.append(f"**{index})** {item}")

    if iteration == 1:
        private_group = "🔥 **ETH TOP 5 ~ 25K** 🔥\n\n" + "\n".join(result)
        standard_group = "🔥 **ETH TOP 5 ~ 25K** 🔥\n\n" + "\n\n".join(result_standard)
    elif iteration == 2:
        private_group = "🔥 **ETH TOP 5 ~ 50K** 🔥\n\n" + "\n".join(result)
        standard_group = "🔥 **ETH TOP 5 ~ 50K** 🔥\n\n" + "\n\n".join(result_standard)
    elif iteration == 3:
        private_group = "🔥 **ETH TOP 5 ~ 100K** 🔥\n\n" + "\n".join(result)
        standard_group = "🔥 **ETH TOP 5 ~ 100K** 🔥\n\n" + "\n\n".join(result_standard)
    elif iteration == 4:
        private_group = "🔥 **ETH TOP 5 ~ 250K** 🔥\n\n" + "\n".join(result)
        standard_group = "🔥 **ETH TOP 5 ~ 250K** 🔥\n\n" + "\n\n".join(result_standard)
    elif iteration == 5:
        private_group = "🔥 **ETH TOP 5 ~ 500K** 🔥\n\n" + "\n".join(result)
        standard_group = "🔥 **ETH TOP 5 ~ 500K** 🔥\n\n" + "\n\n".join(result_standard)
    elif iteration == 6:
        private_group = "🔥 **ETH TOP 5 ~ 1M** 🔥\n\n" + "\n".join(result)
        standard_group = "🔥 **ETH TOP 5 ~ 1M** 🔥\n\n" + "\n\n".join(result_standard)
    elif iteration == 7:
        private_group = "🔥 **ETH TOP 5 ~ 2M** 🔥\n\n" + "\n".join(result)
        standard_group = "🔥 **ETH TOP 5 ~ 2M** 🔥\n\n" + "\n\n".join(result_standard)
    elif iteration == 8:
        private_group = "🔥 **ETH TOP 5 ~ 5M** 🔥\n\n" + "\n".join(result)
        standard_group = "🔥 **ETH TOP 5 ~ 5M** 🔥\n\n" + "\n\n".join(result_standard)


    private_group = private_group + "\n⚡️ `Powered By Hedex` ⚡️\n🤖 @HedexPortalBot 🤖"
    standard_group = standard_group + "\n⚡️ `Powered By Hedex` ⚡️\n🤖 @HedexPortalBot 🤖"

    return private_group, standard_group


async def auto_third_point(html, iteration):
    soup = BeautifulSoup(html, 'html.parser')

    body = list()
    body_standard = list()
    hrefs = list()
    result = list()
    result_standard = list()
    contract_addresses = list()

    table_div = soup.find('div', class_='ds-dex-table ds-dex-table-top')
    a_elements = table_div.find_all('a', class_='ds-dex-table-row ds-dex-table-row-top')


    for a_element in a_elements[:5]:
        chain = a_element.find('img', class_='ds-dex-table-row-chain-icon')['title']
        pair = a_element.find('span', class_='ds-dex-table-row-base-token-symbol').get_text()
        pair += "/" + a_element.find('span', class_='ds-dex-table-row-quote-token-symbol').get_text()
        address = a_element['href'].split('/')[-1]


        daily_percentage_change = a_element.find_all('div', class_='ds-table-data-cell ds-dex-table-row-col-price-change')
        try:
            price_changes = daily_percentage_change[-1].find_all('span', class_='ds-change-perc ds-change-perc-pos')
            price_change = price_changes[-1].get_text()
            body.append(f"{pair} 📈 {price_change} - `{address}`\n" + f"📊 Chart: [Dextools](https://www.dextools.io/app/en/ether/pair-explorer/{address}) | [Dexscreener](https://dexscreener.com/ethereum/{address})\n")
            contract_addresses.append(address)
            body_standard.append(f"{pair} 📈 {price_change} - `{address}`\n" + f"📊 Chart: [Dextools](https://www.dextools.io/app/en/ether/pair-explorer/{address}) | [Dexscreener](https://dexscreener.com/ethereum/{address})\n")
            hrefs.append("https://dexscreener.com" + a_element['href'])
        except:
            price_changes = daily_percentage_change[-1].find_all('span', class_='ds-change-perc ds-change-perc-neg')
            price_change = price_changes[-1].get_text()
            body.append(f"{pair} 📉 {price_change} - `{address}`\n" + f"📊 Chart: [Dextools](https://www.dextools.io/app/en/ether/pair-explorer/{address}) | [Dexscreener](https://dexscreener.com/ethereum/{address})\n")
            contract_addresses.append(address)
            body_standard.append(f"{pair} 📉 {price_change} - `{address}`\n" + f"📊 Chart: [Dextools](https://www.dextools.io/app/en/ether/pair-explorer/{address}) | [Dexscreener](https://dexscreener.com/ethereum/{address})\n")
            hrefs.append("https://dexscreener.com" + a_element['href'])


    for index, item in enumerate(body, 1):
        if index == 1:
            result.append(f"🥇{item}")
        elif index == 2:
            result.append(f"🥈{item}")
        elif index == 3:
            result.append(f"🥉{item}")
        else:
            result.append(f"**{index})** {item}")

    for index, item in enumerate(body_standard, 1):
        if index == 1:
            result_standard.append(f"🥇{item}")
        elif index == 2:
            result_standard.append(f"🥈{item}")
        elif index == 3:
            result_standard.append(f"🥉{item}")
        else:
            result_standard.append(f"**{index})** {item}")

    if iteration == 1:
        private_group = "🔥 **ETH TOP 5 ~ 25K** 🔥\n\n" + "\n".join(result)
        standard_group = "🔥 **ETH TOP 5 ~ 25K** 🔥\n\n" + "\n\n".join(result_standard)
    elif iteration == 2:
        private_group = "🔥 **ETH TOP 5 ~ 50K** 🔥\n\n" + "\n".join(result)
        standard_group = "🔥 **ETH TOP 5 ~ 50K** 🔥\n\n" + "\n\n".join(result_standard)
    elif iteration == 3:
        private_group = "🔥 **ETH TOP 5 ~ 100K** 🔥\n\n" + "\n".join(result)
        standard_group = "🔥 **ETH TOP 5 ~ 100K** 🔥\n\n" + "\n\n".join(result_standard)
    elif iteration == 4:
        private_group = "🔥 **ETH TOP 5 ~ 250K** 🔥\n\n" + "\n".join(result)
        standard_group = "🔥 **ETH TOP 5 ~ 250K** 🔥\n\n" + "\n\n".join(result_standard)
    elif iteration == 5:
        private_group = "🔥 **ETH TOP 5 ~ 500K** 🔥\n\n" + "\n".join(result)
        standard_group = "🔥 **ETH TOP 5 ~ 500K** 🔥\n\n" + "\n\n".join(result_standard)
    elif iteration == 6:
        private_group = "🔥 **ETH TOP 5 ~ 1M** 🔥\n\n" + "\n".join(result)
        standard_group = "🔥 **ETH TOP 5 ~ 1M** 🔥\n\n" + "\n\n".join(result_standard)
    elif iteration == 7:
        private_group = "🔥 **ETH TOP 5 ~ 2M** 🔥\n\n" + "\n".join(result)
        standard_group = "🔥 **ETH TOP 5 ~ 2M** 🔥\n\n" + "\n\n".join(result_standard)
    elif iteration == 8:
        private_group = "🔥 **ETH TOP 5 ~ 5M** 🔥\n\n" + "\n".join(result)
        standard_group = "🔥 **ETH TOP 5 ~ 5M** 🔥\n\n" + "\n\n".join(result_standard)


    private_group = private_group + "\n⚡️ `Powered By Hedex` ⚡️\n🤖 @HedexPortalBot 🤖"
    standard_group = standard_group + "\n⚡️ `Powered By Hedex` ⚡️\n🤖 @HedexPortalBot 🤖"

    return private_group, standard_group, contract_addresses


async def auto_second_point(html, contract_address):
    soup = BeautifulSoup(html, 'html.parser')

    private_template = list()
    standard_template = list()
    wallet_addresses = list()

    coin_pair_element = soup.find('h2', class_='chakra-heading custom-hvdbl1')

    coin_pair = coin_pair_element.text
    coin_pair = coin_pair.replace("Copy token address", "")

    block_txns = soup.find('div', class_='custom-17mi4hx')

    txns = block_txns.find_all('div', class_='custom-kfd3si')

    index = 0
    for txn in txns:
        href = txn.find('a')['href']
        wallet = href.split('/')[-1]
        try:
            bought = txn.find('span', class_="chakra-text custom-rcecxm").get_text().strip()
            try:
                txs = txn.find_all('span', class_="chakra-text custom-13ppmr2")[0].get_text().strip()
                bought_txns = "({})".format(txs.split()[0].split('/')[-1] + " txns")
            except:
                bought_txns = ''
        except:
            bought = "N/A"
            bought_txns = ''

        try:
            sold = txn.find('span', class_="chakra-text custom-dv3t8y").get_text().strip()
        except:
            sold = "N/A"
        try:
            if bought == "N/A":
                try:
                    txs = txn.find_all('span', class_="chakra-text custom-13ppmr2")[0].get_text().strip()
                    sold_txns = "({})".format(txs.split()[0].split('/')[-1] + " txns")
                except:
                    sold_txns = ''
            else:
                txs = txn.find_all('span', class_="chakra-text custom-13ppmr2")[1].get_text().strip()
                sold_txns = "({})".format(txs.split()[0].split('/')[-1] + " txns")
        except:
            sold_txns = ''

        try:
            pnl = txn.find('div', class_="custom-1e9y0rl").get_text().strip()
        except:
            pnl = "N/A"

        try:
            unrealized = txn.find('div', class_="custom-1hd7h4r").get_text().strip()
            if unrealized == "-":
                unrealized = "N/A"
        except:
            unrealized = "N/A"

        try:
            balance_element = txn.find('div', class_="custom-1cicvqe").get_text().strip()
            balance = " of ".join(balance_element.split("of"))
        except:
            balance = "Unknown"

        if bought == "N/A" or sold == "N/A":
            pass
        else:
            check_bought = bought.replace("$", "").replace(",", ".").replace("<", "").replace(">", "")
            check_sold = sold.replace("$", "").replace(",", ".").replace("<", "").replace(">", "")

            if "K" in check_bought:
                check_bought = float(check_bought.replace("K", "")) * 1000
            elif "M" in check_bought:
                check_bought = float(check_bought.replace("M", "")) * 1000000
            else:
                check_bought = float(check_bought)
            if "K" in check_sold:
                check_sold = float(check_sold.replace("K", "")) * 1000
            elif "M" in check_sold:
                check_sold = float(check_sold.replace("M", "")) * 1000000
            else:
                check_sold = float(check_sold)


            difference = abs(check_bought - check_sold)
            threshold_20_percent = 0.2 * min(check_bought, check_sold)

            if difference > threshold_20_percent:
                wallet_addresses.append(wallet)
                index += 1
                if index == 1:
                    private_template.append(f"🥇**Wallet:** `{wallet}`\n🔗 : [Etherscan](https://etherscan.io/address/{wallet})\n\n🔥**Bought:** {bought} {bought_txns}\n❌**Sold:** {sold} {sold_txns}\n📊**PNL:** {pnl}\n🚀**Unrealized:** {unrealized}\n💰**Balance:** {balance}\n")
                    standard_template.append(f"🥇**Wallet:** [0x..(Upgrade to Premium)](https://t.me/HedexPortalBot)\n\n🔥**Bought:** {bought} {bought_txns}\n❌**Sold:** {sold} {sold_txns}\n📊**PNL:** {pnl}\n🚀**Unrealized:** {unrealized}\n💰**Balance:** {balance}\n")
                elif index == 2:
                    private_template.append(f"🥈**Wallet:** `{wallet}`\n🔗 : [Etherscan](https://etherscan.io/address/{wallet})\n\n🔥**Bought:** {bought} {bought_txns}\n❌**Sold:** {sold} {sold_txns}\n📊**PNL:** {pnl}\n🚀**Unrealized:** {unrealized}\n💰**Balance:** {balance}\n")
                    standard_template.append(f"🥈**Wallet:** [0x..(Upgrade to Premium)](https://t.me/HedexPortalBot)\n\n🔥**Bought:** {bought} {bought_txns}\n❌**Sold:** {sold} {sold_txns}\n📊**PNL:** {pnl}\n🚀**Unrealized:** {unrealized}\n💰**Balance:** {balance}\n")
                elif index == 3:
                    private_template.append(f"🥉**Wallet:** `{wallet}`\n🔗 : [Etherscan](https://etherscan.io/address/{wallet})\n\n🔥**Bought:** {bought} {bought_txns}\n❌**Sold:** {sold} {sold_txns}\n📊**PNL:** {pnl}\n🚀**Unrealized:** {unrealized}\n💰**Balance:** {balance}\n")
                    standard_template.append(f"🥉**Wallet:** [0x..(Upgrade to Premium)](https://t.me/HedexPortalBot)\n\n🔥**Bought:** {bought} {bought_txns}\n❌**Sold:** {sold} {sold_txns}\n📊**PNL:** {pnl}\n🚀**Unrealized:** {unrealized}\n💰**Balance:** {balance}\n")
                else:
                    private_template.append(f"**RANK #{index}**\n**Wallet:** `{wallet}`\n🔗 : [Etherscan](https://etherscan.io/address/{wallet})\n\n🔥**Bought:** {bought} {bought_txns}\n❌**Sold:** {sold} {sold_txns}\n📊**PNL:** {pnl}\n🚀**Unrealized:** {unrealized}\n💰**Balance:** {balance}\n")
                    standard_template.append(f"**RANK #{index}**\n**Wallet:** [0x..(Upgrade to Premium)](https://t.me/HedexPortalBot)\n\n🔥**Bought:** {bought} {bought_txns}\n❌**Sold:** {sold} {sold_txns}\n📊**PNL:** {pnl}\n🚀**Unrealized:** {unrealized}\n💰**Balance:** {balance}\n")
            else:
                pass

    try:
        coin = coin_pair.split("/")[0]
        current_wallet_addresses = [wlt.lower() for wlt in wallet_addresses[:3]]
        for wallet_adr in current_wallet_addresses:
            list_of_wallet_addresses_from_db = get_wallet_list()
            if wallet_adr not in list_of_wallet_addresses_from_db and len(wallet_adr) > 0:
                add_wallet_to_wallets_db(wallet_adr)
            add_contract_to_wallet_list(wallet_adr, contract_address, coin)
            print(f"added\nwallet: {wallet_adr}\ncontract: {contract_address}\ncoin: {coin}\n")
    except Exception as error:
        print(f"Error in adding contract to wallet list, error:\n{error}")

    private_group = f"`${coin_pair}`\n\n📄Contract:\n`{contract_address}`\n\n" + f"📈 Chart: [Dextools](https://www.dextools.io/app/en/ether/pair-explorer/{contract_address}) | [Dexscreener](https://dexscreener.com/ethereum/{contract_address})\n\n" + "\n".join(private_template[:3])
    standard_group = f"`${coin_pair}`\n\n📄Contract:\n`{contract_address}`\n\n" + f"📈 Chart: [Dextools](https://www.dextools.io/app/en/ether/pair-explorer/{contract_address}) | [Dexscreener](https://dexscreener.com/ethereum/{contract_address})\n\n" + "\n".join(standard_template[:3])

    private_group = private_group + "\n⚡️ `Powered By Hedex` ⚡️\n🤖 @HedexPortalBot 🤖"
    standard_group = standard_group + "\n⚡️ `Powered By Hedex` ⚡️\n🤖 @HedexPortalBot 🤖"

    return private_group, standard_group, wallet_addresses[:3]
