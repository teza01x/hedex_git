import time
import asyncio
import sys
from DrissionPage import ChromiumPage, ChromiumOptions
from config import *


async def first_pass_cycle(wallet_address):
    sys.stdout.reconfigure(encoding='utf-8')
    browser_path = path_to_browser

    options = ChromiumOptions()
    options.set_paths(browser_path=browser_path)

    arguments = [
        "-no-first-run",
        "-force-color-profile=srgb",
        "-metrics-recording-only",
        "-password-store=basic",
        "-use-mock-keychain",
        "-export-tagged-pdf",
        "-no-default-browser-check",
        "-disable-background-mode",
        "-enable-features=NetworkService,NetworkServiceInProcess,LoadCryptoTokenExtension,PermuteTLSExtensions",
        "-disable-features=FlashDeprecationWarning,EnablePasswordsAccountStorage",
        "-deny-permission-prompts",
        "-disable-gpu"
        "-headless=new"
        "-incognito"
    ]

    for argument in arguments:
        options.set_argument(argument)


    driver = ChromiumPage(addr_driver_opts=options)

    html = driver.html

    tabs = driver.tabs
    if len(tabs) == limit_queue:
        return "busy"


    url = f'https://dexcheck.ai/app/address-analyzer/{wallet_address}?timeframe=90'

    driver.to_tab(driver.new_tab(url))
    tab_id = driver.tab_id
    tabs = driver.tabs


    while True:
        try:
            spinner = driver('xpath://div/iframe').ele("xpath://*[@id='challenge-stage']/div/label/input", timeout=0.1)
            if spinner:
                print("get spinner")
                spinner.click()
        except:
            try:
                ele = driver.s_ele('xpath://p[@class="mr-1 text-lg font-semibold text-white sm:text-2xl"]')
                if ele.text == "Address:":
                    break
            except:
                await asyncio.sleep(1)
                driver.to_tab(tab_id)

    await asyncio.sleep(30)
    driver.to_tab(tab_id)
    html = driver.html

    tabs = driver.tabs
    if len(tabs) > 1:
        driver.close_tabs(tabs_or_ids=tab_id)


    return "free", html


async def first_pass_cycle_part2(wallet_address):
    sys.stdout.reconfigure(encoding='utf-8')
    browser_path = path_to_browser

    options = ChromiumOptions()
    options.set_paths(browser_path=browser_path)

    arguments = [
        "-no-first-run",
        "-force-color-profile=srgb",
        "-metrics-recording-only",
        "-password-store=basic",
        "-use-mock-keychain",
        "-export-tagged-pdf",
        "-no-default-browser-check",
        "-disable-background-mode",
        "-enable-features=NetworkService,NetworkServiceInProcess,LoadCryptoTokenExtension,PermuteTLSExtensions",
        "-disable-features=FlashDeprecationWarning,EnablePasswordsAccountStorage",
        "-deny-permission-prompts",
        "-disable-gpu"
        "-headless=new"
        "-incognito"
    ]

    for argument in arguments:
        options.set_argument(argument)


    driver = ChromiumPage(addr_driver_opts=options)

    html = driver.html

    tabs = driver.tabs
    if len(tabs) == limit_queue:
        return "busy"

    url = f'https://etherscan.io/address/{wallet_address}'

    driver.to_tab(driver.new_tab(url))
    tab_id = driver.tab_id
    tabs = driver.tabs

    await asyncio.sleep(10)
    driver.to_tab(tab_id)
    html = driver.html

    tabs = driver.tabs
    if len(tabs) > 1:
        driver.close_tabs(tabs_or_ids=tab_id)


    return "free", html


async def second_pass_cycle(contract_address):
    sys.stdout.reconfigure(encoding='utf-8')
    browser_path = path_to_browser

    options = ChromiumOptions()
    options.set_paths(browser_path=browser_path)

    arguments = [
        "-no-first-run",
        "-force-color-profile=srgb",
        "-metrics-recording-only",
        "-password-store=basic",
        "-use-mock-keychain",
        "-export-tagged-pdf",
        "-no-default-browser-check",
        "-disable-background-mode",
        "-enable-features=NetworkService,NetworkServiceInProcess,LoadCryptoTokenExtension,PermuteTLSExtensions",
        "-disable-features=FlashDeprecationWarning,EnablePasswordsAccountStorage",
        "-deny-permission-prompts",
        "-disable-gpu"
        "-headless=new"
        "-incognito"
    ]

    for argument in arguments:
        options.set_argument(argument)


    driver = ChromiumPage(addr_driver_opts=options)

    html = driver.html

    tabs = driver.tabs
    if len(tabs) == limit_queue:
        return "busy"

    url = f'https://dexscreener.com/ethereum/{contract_address}'

    driver.to_tab(driver.new_tab(url))
    tab_id = driver.tab_id
    tabs = driver.tabs

    while True:
        try:
            spinner = driver('xpath://div/iframe').ele("xpath://*[@id='challenge-stage']/div/label/input", timeout=0.1)
            if spinner:
                print("get spinner")
                spinner.click()
            elif spinner == None:
                try:
                    ele = driver.s_ele('xpath://span[@class="chakra-text custom-12v4f4h"]')
                    if ele.text == "SCREENER":
                        break
                except:
                    pass
        except:
            try:
                ele = driver.s_ele('xpath://span[@class="chakra-text custom-12v4f4h"]')
                if ele.text == "SCREENER":
                    break
            except:
                await asyncio.sleep(1)
                driver.to_tab(tab_id)

    await asyncio.sleep(5)
    driver.to_tab(tab_id)


    button = driver.ele('xpath://button[@class="chakra-button custom-1tgk3lm"]', timeout=0.1)
    if button:
        button.click(by_js=True)
        await asyncio.sleep(2)
        driver.to_tab(tab_id)

    html = driver.html

    tabs = driver.tabs
    if len(tabs) > 1:
        driver.close_tabs(tabs_or_ids=tab_id)


    return "free", html


async def third_pass_cycle(url):
    sys.stdout.reconfigure(encoding='utf-8')
    browser_path = path_to_browser

    options = ChromiumOptions()
    options.set_paths(browser_path=browser_path)

    arguments = [
        "-no-first-run",
        "-force-color-profile=srgb",
        "-metrics-recording-only",
        "-password-store=basic",
        "-use-mock-keychain",
        "-export-tagged-pdf",
        "-no-default-browser-check",
        "-disable-background-mode",
        "-enable-features=NetworkService,NetworkServiceInProcess,LoadCryptoTokenExtension,PermuteTLSExtensions",
        "-disable-features=FlashDeprecationWarning,EnablePasswordsAccountStorage",
        "-deny-permission-prompts",
        "-disable-gpu"
        "-headless=new"
        "-incognito"
    ]

    for argument in arguments:
        options.set_argument(argument)


    driver = ChromiumPage(addr_driver_opts=options)

    html = driver.html

    tabs = driver.tabs
    if len(tabs) == limit_queue:
        return "busy"

    driver.to_tab(driver.new_tab(url))
    tab_id = driver.tab_id
    tabs = driver.tabs

    while True:
        try:
            spinner = driver('xpath://div/iframe').ele("xpath://*[@id='challenge-stage']/div/label/input", timeout=0.1)
            if spinner:
                print("get spinner")
                spinner.click()
        except:
            try:
                ele = driver.s_ele('xpath://span[@class="chakra-text custom-12v4f4h"]')
                if ele.text == "SCREENER":
                    break
            except:
                await asyncio.sleep(1)
                driver.to_tab(tab_id)

    await asyncio.sleep(10)
    driver.to_tab(tab_id)
    html = driver.html

    tabs = driver.tabs
    if len(tabs) > 1:
        driver.close_tabs(tabs_or_ids=tab_id)


    return "free", html


def auto_second_pass_cycle(contract_address):
    sys.stdout.reconfigure(encoding='utf-8')
    browser_path = path_to_browser

    options = ChromiumOptions()
    options.set_paths(browser_path=browser_path)

    arguments = [
        "-no-first-run",
        "-force-color-profile=srgb",
        "-metrics-recording-only",
        "-password-store=basic",
        "-use-mock-keychain",
        "-export-tagged-pdf",
        "-no-default-browser-check",
        "-disable-background-mode",
        "-enable-features=NetworkService,NetworkServiceInProcess,LoadCryptoTokenExtension,PermuteTLSExtensions",
        "-disable-features=FlashDeprecationWarning,EnablePasswordsAccountStorage",
        "-deny-permission-prompts",
        "-disable-gpu"
        "-headless=new"
        "-incognito"
    ]

    for argument in arguments:
        options.set_argument(argument)


    driver = ChromiumPage(addr_driver_opts=options)

    html = driver.html

    tabs = driver.tabs
    if len(tabs) == limit_queue:
        return "busy"

    url = f'https://dexscreener.com/ethereum/{contract_address}'

    driver.to_tab(driver.new_tab(url))
    tab_id = driver.tab_id
    tabs = driver.tabs

    while True:
        try:
            spinner = driver('xpath://div/iframe').ele("xpath://*[@id='challenge-stage']/div/label/input", timeout=0.1)
            if spinner:
                print("get spinner")
                spinner.click()
            elif spinner == None:
                try:
                    ele = driver.s_ele('xpath://span[@class="chakra-text custom-12v4f4h"]')
                    if ele.text == "SCREENER":
                        break
                except:
                    pass
        except:
            try:
                ele = driver.s_ele('xpath://span[@class="chakra-text custom-12v4f4h"]')
                if ele.text == "SCREENER":
                    break
            except:
                time.sleep(1)
                driver.to_tab(tab_id)

    time.sleep(5)
    driver.to_tab(tab_id)


    button = driver.ele('xpath://button[@class="chakra-button custom-1tgk3lm"]', timeout=0.1)
    if button:
        button.click(by_js=True)
        time.sleep(2)
        driver.to_tab(tab_id)

    html = driver.html

    tabs = driver.tabs
    if len(tabs) > 1:
        driver.close_tabs(tabs_or_ids=tab_id)


    return "free", html


def auto_third_pass_cycle(url):
    sys.stdout.reconfigure(encoding='utf-8')
    browser_path = path_to_browser

    options = ChromiumOptions()
    options.set_paths(browser_path=browser_path)

    arguments = [
        "-no-first-run",
        "-force-color-profile=srgb",
        "-metrics-recording-only",
        "-password-store=basic",
        "-use-mock-keychain",
        "-export-tagged-pdf",
        "-no-default-browser-check",
        "-disable-background-mode",
        "-enable-features=NetworkService,NetworkServiceInProcess,LoadCryptoTokenExtension,PermuteTLSExtensions",
        "-disable-features=FlashDeprecationWarning,EnablePasswordsAccountStorage",
        "-deny-permission-prompts",
        "-disable-gpu"
        "-headless=new"
        "-incognito"
    ]

    for argument in arguments:
        options.set_argument(argument)


    driver = ChromiumPage(addr_driver_opts=options)

    html = driver.html

    tabs = driver.tabs
    if len(tabs) == limit_queue:
        return "busy"

    driver.to_tab(driver.new_tab(url))
    tab_id = driver.tab_id

    while True:
        try:
            spinner = driver('xpath://div/iframe').ele("xpath://*[@id='challenge-stage']/div/label/input", timeout=0.1)
            if spinner:
                print("get spinner")
                spinner.click()
        except:
            try:
                ele = driver.s_ele('xpath://span[@class="chakra-text custom-12v4f4h"]')
                if ele.text == "SCREENER":
                    break
            except:
                time.sleep(1)
                driver.to_tab(tab_id)

    time.sleep(10)
    driver.to_tab(tab_id)
    html = driver.html

    tabs = driver.tabs
    if len(tabs) > 1:
        driver.close_tabs(tabs_or_ids=tab_id)


    return "free", html


def auto_first_pass_cycle(wallet_address):
    sys.stdout.reconfigure(encoding='utf-8')
    browser_path = path_to_browser

    options = ChromiumOptions()
    options.set_paths(browser_path=browser_path)

    arguments = [
        "-no-first-run",
        "-force-color-profile=srgb",
        "-metrics-recording-only",
        "-password-store=basic",
        "-use-mock-keychain",
        "-export-tagged-pdf",
        "-no-default-browser-check",
        "-disable-background-mode",
        "-enable-features=NetworkService,NetworkServiceInProcess,LoadCryptoTokenExtension,PermuteTLSExtensions",
        "-disable-features=FlashDeprecationWarning,EnablePasswordsAccountStorage",
        "-deny-permission-prompts",
        "-disable-gpu"
        "-headless=new"
        "-incognito"
    ]

    for argument in arguments:
        options.set_argument(argument)


    driver = ChromiumPage(addr_driver_opts=options)

    html = driver.html

    tabs = driver.tabs
    if len(tabs) == limit_queue:
        return "busy"

    url = f'https://dexcheck.ai/app/address-analyzer/{wallet_address}?timeframe=90'

    driver.to_tab(driver.new_tab(url))
    tab_id = driver.tab_id
    tabs = driver.tabs


    while True:
        try:
            spinner = driver('xpath://div/iframe').ele("xpath://*[@id='challenge-stage']/div/label/input", timeout=0.1)
            if spinner:
                print("get spinner")
                spinner.click()
        except:
            try:
                ele = driver.s_ele('xpath://p[@class="mr-1 text-lg font-semibold text-white sm:text-2xl"]')
                if ele.text == "Address:":
                    break
            except:
                time.sleep(1)
                driver.to_tab(tab_id)

    time.sleep(30)
    driver.to_tab(tab_id)
    html = driver.html

    tabs = driver.tabs
    if len(tabs) > 1:
        driver.close_tabs(tabs_or_ids=tab_id)


    return "free", html


def off_driver_func():
    sys.stdout.reconfigure(encoding='utf-8')
    browser_path = path_to_browser

    options = ChromiumOptions()
    options.set_paths(browser_path=browser_path)

    arguments = [
        "-no-first-run",
        "-force-color-profile=srgb",
        "-metrics-recording-only",
        "-password-store=basic",
        "-use-mock-keychain",
        "-export-tagged-pdf",
        "-no-default-browser-check",
        "-disable-background-mode",
        "-enable-features=NetworkService,NetworkServiceInProcess,LoadCryptoTokenExtension,PermuteTLSExtensions",
        "-disable-features=FlashDeprecationWarning,EnablePasswordsAccountStorage",
        "-deny-permission-prompts",
        "-disable-gpu"
        "-headless=new"
        "-incognito"
    ]

    for argument in arguments:
        options.set_argument(argument)


    driver = ChromiumPage(addr_driver_opts=options)

    html = driver.html

    time.sleep(10)

    driver.quit()
