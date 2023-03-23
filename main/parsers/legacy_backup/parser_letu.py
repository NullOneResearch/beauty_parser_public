import database.database_handler as db_handler
#import parsers.database.database_handler as db_handler
import re
import requests
import json
import time
import pandas as pd
from bs4 import BeautifulSoup
from datetime import date

import logging
import random

import warnings

from time import sleep

import requests
import random

from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.proxy import Proxy, ProxyType

import os
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

def log_progress(sequence, every=None, size=None, name='Items'):
    from ipywidgets import IntProgress, HTML, VBox
    from IPython.display import display

    is_iterator = False
    if size is None:
        try:
            size = len(sequence)
        except TypeError:
            is_iterator = True
    if size is not None:
        if every is None:
            if size <= 200:
                every = 1
            else:
                #every = int(size / 200)     # every 0.5%
                every = 1
    else:
        assert every is not None, 'sequence is iterator, set every'

    if is_iterator:
        progress = IntProgress(min=0, max=1, value=1)
        progress.bar_style = 'info'
    else:
        progress = IntProgress(min=0, max=size, value=0)
    label = HTML()
    box = VBox(children=[label, progress])
    display(box)

    index = 0
    try:
        for index, record in enumerate(sequence, 1):
            if index == 1 or index % every == 0:
                if is_iterator:
                    label.value = '{name}: {index} / ?'.format(
                        name=name,
                        index=index
                    )
                else:
                    progress.value = index
                    label.value = u'{name}: {index} / {size}'.format(
                        name=name,
                        index=index,
                        size=size
                    )
            yield record
    except:
        progress.bar_style = 'danger'
        raise
    else:
        progress.bar_style = 'success'
        progress.value = index
        label.value = "{name}: {index}".format(
            name=name,
            index=str(index or '?')
        )

def has_numbers(inputString):
    return any(char.isdigit() for char in inputString)

def get_cookie(current_proxy):
    # есть риск ловли чистой еррор страницы, лучше трай-эксепты фигануть вокруг селениума
    # хотя в принципе в логике большого парсера логика должна работать стабильно
    # тут есть возможность юзать прокси для https и получения кук, но поведение сайтов аномальное
    try:
        proxy_check = True

        caps = DesiredCapabilities().FIREFOX
        caps['pageLoadStrategy'] = 'eager'

        if proxy_check == True:
            # отключить если нет блока по айпи
            caps['proxy'] = {
                "proxyType": "MANUAL",
                "httpProxy": current_proxy,
                #"socksProxy":current_proxy,
                "sslProxy": current_proxy,
            }
            caps['acceptInsecureCerts']=True

        binary = FirefoxBinary(r'C:\Program Files\Mozilla Firefox\firefox.exe')
        gecko = os.path.normpath(r'C:\Program Files\Mozilla Firefox\\geckodriver.exe')

        driver = webdriver.Firefox(firefox_binary=binary, executable_path=gecko, desired_capabilities=caps)
        driver.set_page_load_timeout(10)
        wait = WebDriverWait(driver, 1)

        url = 'https://www.letu.ru/'
        driver.get(url)

        soup = BeautifulSoup(driver.page_source, 'lxml')

        all_cookies=driver.get_cookies();
        cookies_dict = {}
        for cookie in all_cookies:
            cookies_dict[cookie['name']] = cookie['value']
        print(cookies_dict)

        z = 0
        while len(cookies_dict) == 0:
            time.sleep(1)

            all_cookies=driver.get_cookies();
            cookies_dict = {}
            for cookie in all_cookies:
                cookies_dict[cookie['name']] = cookie['value']
            print(cookies_dict)
            z+=1
            if z > 4:
                break

        # ждем пока длина будет ок, затем получаем куки и закрываем

        #driver.close()
        driver.quit()
    except Exception as e: # сюда фигануть конструкцию на проверку ошибки, чтобы был только рантайм еррор и что страница ошибки
        # трай-эксепт тут нужен чисто чтобы нормально закрыть браузер
        print('getting_cookies_error: ', e)
        #logger.info("getting_cookies_error: {%s}", e)
        # driver.close()
        driver.quit()
        stop

    return cookies_dict

def get_proxy_and_cookie():
    # скрипт получения прокси и куки
    while True:
        try:
            break_check_layer_1 = 0
            curent_proxy = list_of_proxies[random.randint(0,len(list_of_proxies)-1)]
            print('using proxy:', curent_proxy)
            proxies = {
               'https': curent_proxy,
            }

            # нужно автоматизировать кейсы когда прокси отваливаются, чтобы не терять прогресса
            cookies_dict = get_cookie(curent_proxy)
            break_check_layer_1 = 1
        except Exception as e:
            print(e)
        if break_check_layer_1 == 1 and cookies_dict != {}:
            break

    return curent_proxy, cookies_dict, proxies

def get_previous_results(prev_sku_exists_check):
    # тут можно сделать ситуативный рестарт от определенного валью через исключение уже спарсенных значений
    if prev_sku_exists_check == False:
        acquired_sku_s = [] #  !!!!!!! сделать автонаполнение акваерд ску перед стартом
        all_products_from_list = []
    else:
        try:
            with open('data_letu_'+str(today)+'.json', 'rb') as fp:
                all_products_from_list = json.load(fp)

            acquired_sku_s = []

            for iter_acq_skus in all_products_from_list:
                acquired_sku_s.append(iter_acq_skus['id'])
        except:
            print('prev sku does not exist')
            acquired_sku_s = []

    return acquired_sku_s, all_products_from_list

with open('misc/list_of_proxies.json', 'rb') as fp:
    list_of_proxies = json.load(fp)

logging.basicConfig(filename='misc/logs.json', filemode='a+', level=logging.INFO)
logger = logging.getLogger()

headers = {
    'Content-Type': 'application/json',
}

response = requests.get('https://www.letu.ru/productSitemapRU.xml')

#response.text
parsed_xml_list = response.text.replace('</loc>', '<loc>').split('<loc>')
filtered_parsed_list = []

for i in parsed_xml_list:
    # чекаем чтобы был дефис, чекаем чтобы были цифры, чекаем чтобы не было лишних категорий, чекаем чтобы в мапинге первым элементов была цифра
    if 'letu.ru' in i:
        filtered_parsed_list.append(i)

response = requests.get('https://www.letu.ru/productChanelSitemapRU.xml')
parsed_xml_list = response.text.replace('</loc>', '<loc>').split('<loc>')

for i in parsed_xml_list:
    if 'letu.ru' in i:
        filtered_parsed_list.append(i)


target_sku_list = []
for iter_filtered_parsed_list in filtered_parsed_list:
    target_sku_list.append(iter_filtered_parsed_list.split('/')[-1])

# первое разовое получение куки
# выбор первого рандомного прокси
# это тоже можно в while загнать

curent_proxy, cookies_dict, proxies = get_proxy_and_cookie()

# этот момент надо будет доработать перед тем как в продовый скрипт заливать
# сперва проверить - существует ли за сегодня и за вчера файл, и затем уже его открывать
# дополнительно - сделать доп проверку на момент получения данных, в отдельный столбик,
# и обновлять только те данные, которым больше чем 2 дня

#with open('data_letu_'+str(today)+'.json', 'rb') as fp:
#    parsed_letu_data = json.load(fp)

#for iter_acq_skus in parsed_letu_data:
#    acquired_sku_s.append(iter_acq_skus['id'])

#acquired_sku_s

# сделать автонаполнение акваерд ску перед стартом
# можно добавить дату добавления и ориентироваться по ней

# скрипт зависает при длительном прогоне, похоже что ловит бесконечный цикл
# нужна функция для проверки веллбиинг скрипта и дальнейшего его перезапуска с точки паузы
# + регулярная отгрузка в физическую бд вне кернеля
# вообще это надо к базе данных привязать и обновлять по таймингу от прошлого обновления

# сюда же можно бахнуть скрипт для итеративной загрузки списка проксей каждый прогон
# бахнул, теперь во время прогона можно менять список активных прокси

# парсер на всех


prev_sku_exists_check = True

warnings.filterwarnings('ignore')

#logging.basicConfig(filename='logs.json', filemode='a+', level=logging.INFO)
#logger = logging.getLogger()

# тут можно сделать ситуативный рестарт от определенного валью через исключение уже спарсенных значений
# сюда еще можно дату навернуть
acquired_sku_s, all_products_from_list = get_previous_results(prev_sku_exists_check)

z = 0
counter_for_proxy = 0
url_for_request = 'https://www.letu.ru/s/api/product/v1/products/similar/%s/12'

for target_sku in log_progress(target_sku_list):
    while True:
        try:
            break_check = 0
            if target_sku not in acquired_sku_s: # пробую убрать лишние запросы, но так как нет прямого таргета на предмет -
                # идея такого фильтра довольно сомнительна, лучше идей у меня пока нету
                # тут доп проверку на случай если куки здохло
                response_api = requests.get(url_for_request%target_sku, cookies=cookies_dict, proxies=proxies, timeout=10)

                if 'Payment Required' in response_api.text:
                    with open('misc/list_of_proxies.json', 'rb') as fp:
                        list_of_proxies = json.load(fp)

                    # проверка пейволла
                    now = datetime.now()
                    #print('paywall trouble', now)
                    logger.info("paywall trouble: {%s}", (response_api.text, now))

                    # словил пейволл, меняю прокси
                    curent_proxy, cookies_dict, proxies = get_proxy_and_cookie()

                    response_api = requests.get(url_for_request%target_sku, cookies=cookies_dict, proxies=proxies, timeout=10)
                    CasesJson = json.loads(response_api.text)


                CasesJson = json.loads(response_api.text)

                if 'ERROR' in str(CasesJson):
                    with open('misc/list_of_proxies.json', 'rb') as fp:
                        list_of_proxies = json.load(fp)

                    # проверка ошибки куки в жсоне
                    now = datetime.now()
                    #print("trouble with cookie:", now)
                    logger.info("trouble with cookie: {%s}", now)

                    # меняю куку, просто так ерроры не бывают
                    curent_proxy, cookies_dict, proxies = get_proxy_and_cookie()

                    response_api = requests.get(url_for_request%target_sku, cookies=cookies_dict, proxies=proxies, timeout=10)
                    CasesJson = json.loads(response_api.text)

                # таргет на несколько, но только по одной странице
                try:
                    for product_id in range(0, len(CasesJson['products'])): # тут цифру крч

                        cases_dict = CasesJson['products'][product_id]
                        cases_dict

                        your_keys = ['brandName','categoryId','categoryName','displayName','id','minSkuId','minSkuName',
                            'minSkuPrice','noLongerAvailable','numberOfSkuAvailable','numberOfSkuInStock','price',
                            'priceWithoutCoupons','rating','rawPrice','url','discountPercent','onePriceForAllSkus',]
                        temp_product_dict = { your_key: cases_dict[your_key] for your_key in your_keys }

                        if temp_product_dict['id'] not in acquired_sku_s:
                            #### добавил
                            today = date.today()
                            temp_product_dict['date_acquired'] = today
                            ####

                            all_products_from_list.append(temp_product_dict)
                            acquired_sku_s.append(temp_product_dict['id'])
                except Exception as e:
                    z+=1
                    #print("trouble with sku: {%s}", target_sku, z) # потом вернуть норм логгер и запускать как просто скрипт
                    print(e)
                    logger.info("trouble with sku: {%s}", (target_sku, z))

                counter_for_proxy +=1

            if counter_for_proxy > 1000:
                now = datetime.now()
                #print("save threshold exceeded, proxy change:", now)
                logger.info("save threshold exceeded, proxy change: {%s}", now)

                with open('data_letu_'+str(today)+'.json', 'w', encoding='utf-8') as f:
                    json.dump(all_products_from_list, f, ensure_ascii=False, indent=4)
                #print("saving data")
                logger.info("saving data: {%s}", now)

                # смена прокси каждые N прогонов
                curent_proxy, cookies_dict, proxies = get_proxy_and_cookie()

                # нулим счетчик
                counter_for_proxy = 0

            break_check = 1
        except Exception as e:
            print(e)
            if 'HTTPSConnectionPool' not in str(e):
                stop # ломаем алгоритм если неизвестная ошибка. Вообще это по-другому
                # делается, но сейчас уже 4 утра и я не понимаю как конкретно там
                # выловить нужную ошибку из цепочки 4 ошибок для эксепта
                # в общем пока это для дебага и поиска новых ошибок

            with open('misc/list_of_proxies.json', 'rb') as fp:
                list_of_proxies = json.load(fp)

            now = datetime.now()
            print("proxy failed, changing proxy:", now)
            print('data acquired:', len(all_products_from_list))
            #logger.info("save threshold exceeded, proxy change: {%s}", now)

            # смена прокси
            curent_proxy, cookies_dict, proxies = get_proxy_and_cookie()

        # выходим из цикла while в случае успеха
        if break_check == 1:
            break



today = date.today()

with open('database/json_dumps/data_letu_'+str(today)+'.json', 'w', encoding='utf-8') as f:
    json.dump(all_products_from_list, f, ensure_ascii=False, indent=4)

now = datetime.now()
logger.info("letu done, going to database: {%s}", now)

db_handler.handle_letu(str(today))
