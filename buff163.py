from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

import json
import time
import requests
import undetected_chromedriver as uc



"""
    Функция чтения json-файла

    :param     filename: Название файла
    :type      filename: str.
    
    :returns: dict или list
"""
def json_load(filename):
    with open(filename, "r", encoding="utf8") as read_file:
        result = json.load(read_file)
    return result

"""
    Функция записи в json-файл

    :param     filename: Название файла
    :type      filename: str.
    :param     data: Записываемые данные
    :type      data: list or dict.
  
"""
def json_dump(filename, data):
    with open(filename, "w", encoding="utf8") as write_file:
        json.dump(data, write_file, ensure_ascii=False)




"""
    Функция отправки сообщения в телеграм 

    :param     text: Отправляемый текст сообщения
    :type      text: str.
    :param tg_token: Токен телеграм-бота из BotFather
    :type  tg_token: str.
    :param  user_id: ID пользователя бота
    :type   user_id: int.

"""
def send_msg(text, tg_token, user_id):
    url_req = (
        "https://api.telegram.org/bot"
        + tg_token
        + "/sendMessage"
        + "?chat_id="
        + str(user_id)
        + "&text="
        + text
    )
    requests.get(url_req)



def get_driver_cookies(driver):

    cookies_list = browser.get_cookies()
    cookies_dict = {}
    for cookie in cookies_list:
        cookies_dict[cookie["name"]] = cookie["value"]
    return [cookies_list, cookies_dict]


def check_min_price(session, url, game, price):

    items = session.get(url.format(game, 1)).json()["data"]["items"]
    item = items[0]
    if float(item["sell_min_price"]) == price:
        return [True, items]
    else:
        return [False, items]


def get_driver_cookies(driver):

    cookies_list = browser.get_cookies()
    cookies_dict = {}
    for cookie in cookies_list:
        cookies_dict[cookie["name"]] = cookie["value"]
    return [cookies_list, cookies_dict]


try:
    config         = json_load(r"./json/config.json")
except:
    print('Заполните корректно файл с настройками')


price     = config['price']
game      = config['game']
token     = config['tg_token']
user_id   = config['user_id']


try:
    cookies   = json_load(r"./json/cookies.json")

except:
    print('Заполните корректно файл с куки')


count_of_buys = 0

check_url            = "https://buff.163.com/api/market/goods?game={}&page_num={}&sort_by=price.asc&_=1687181700055"
check_url_for_chrome = "https://buff.163.com/market/{}#tab=selling&page_num={}"
sells_urls = "https://buff.163.com/api/market/goods/sell_order?game={}&goods_id={}&page_num=1&sort_by=default&mode=&allow_tradable_cooldown=1&_=1681817455940"


options = webdriver.ChromeOptions()
options.add_argument("--headless")
browser = uc.Chrome(options=options)

browser.get("https://buff.163.com/")


for cookie in cookies:
    browser.add_cookie(cookie)


while True:
    browser.get(check_url_for_chrome.format(game, 1))

    element_menu = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located(
            (By.CLASS_NAME, "w-Select-Multi.w-Select-scroll.black")
        )
    )

    hover = ActionChains(browser).move_to_element(element_menu)
    hover.click(element_menu)
    hover.perform()

    element_order_by = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "w-Order_asc"))
    )
    hover.move_to_element(element_order_by)
    hover.click(element_order_by)
    hover.perform()
    time.sleep(1)
    list_of_goods_urls = []
    try:
        element = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located(
                (By.CLASS_NAME, "w-Select-Multi.w-Select-scroll.black")
            )
        )
        menu = browser.find_element(
            By.CLASS_NAME, "w-Select-Multi.w-Select-scroll.black"
        )
        menu.click()
        time.sleep(1)
        element = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "w-Order_asc"))
        )
        order_by = menu.find_element(By.CLASS_NAME, "w-Order_asc").click()
    except Exception as e:
        continue

    try:
        element = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "card_{}".format(game)))
        )
        market_card = browser.find_element(By.CLASS_NAME, "card_{}".format(game))
    except Exception as e:
        continue

    list_of_items = market_card.find_elements(By.TAG_NAME, "li")
    for item in list_of_items:
        href = item.find_element(By.TAG_NAME, "a").get_attribute("href")
        goods_price = float(
            item.find_element(By.CLASS_NAME, "f_Strong").text.replace("¥ ", "")
        )

        if goods_price <= price:
            list_of_goods_urls.append(href)
        else:
            break

    if len(list_of_goods_urls) > 0:
        for url in list_of_goods_urls:
            browser.get(url)
            element = WebDriverWait(browser, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, "list_tb"))
            )
            min_price_on_page = float(
                browser.find_element(By.CLASS_NAME, "list_tb")
                .find_element(By.CLASS_NAME, "f_Strong")
                .text.replace("¥ ", "")
            )
            selling_info = browser.find_elements(By.CLASS_NAME, "selling")

            if min_price_on_page <= price:
                for item_on_selling in selling_info:
                    try:
                        item_price = float(
                            item_on_selling.find_element(
                                By.CLASS_NAME, "f_Strong"
                            ).text.replace("¥ ", "")
                        )
                        oreder_id = item_on_selling.get_attribute("data-orderid")
                    except:
                        continue

                    if item_price <= price:
                        try:
                            element = WebDriverWait(browser, 5).until(
                                EC.presence_of_element_located(
                                    (
                                        By.XPATH,
                                        "//a[@data-orderid='{}']".format(oreder_id),
                                    )
                                )
                            )
                            sells = browser.find_element(
                                By.XPATH, "//a[@data-orderid='{}']".format(oreder_id)
                            ).click()
                        except Exception as e:
                            print("Не успел купить")
                            continue

                        try:
                            element = WebDriverWait(browser, 5).until(
                                EC.presence_of_element_located(
                                    (By.XPATH, "//a[@class='i_Btn pay-btn']")
                                )
                            )
                            buy_btn = browser.find_element(
                                By.XPATH, "//a[@class='i_Btn pay-btn']"
                            ).click()
                        except Exception as e:
                            print("Не вылезло подтверждение или не успел купить")
                            continue

                        try:
                            element = WebDriverWait(browser, 5).until(
                                EC.presence_of_element_located(
                                    (By.XPATH, "//a[@id='ask_seller']")
                                )
                            )
                            trade_btn = browser.find_element(
                                By.XPATH, "//a[@id='ask_seller']"
                            ).click()
                        except Exception as e:
                            continue

                        count_of_buys += 1

                        if count_of_buys % 25 == 0:

                            send_msg("Куплено: " + str(count_of_buys),token,user_id)

    json_dump(r"./json/cookies.json", get_driver_cookies(browser))
    browser.refresh()
