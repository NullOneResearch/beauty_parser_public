#import database.database_handler as db_handler
import parsers.database.database_handler as db_handler
import time

list_of_proxies_global_address = 'parsers/misc/list_of_proxies.json'
logs_global_address = 'parsers/misc/logs.json'
path_to_db_global = 'parsers/database/json_dumps'

def parser_gold_apple():
    #
    import requests
    import json
    import pandas as pd
    from datetime import date
    from datetime import datetime
    import logging
    import warnings

    def has_numbers(inputString):
        return any(char.isdigit() for char in inputString)


    headers = {
        'Content-Type': 'application/json',
    }

    response = requests.get('https://goldapple.ru/pub/sitemap-1-1.xml')

    parsed_xml_list = response.text.replace('</loc>', '<loc>').split('<loc>')
    filtered_parsed_list = []

    for i in parsed_xml_list:
        # чекаем чтобы был дефис, чекаем чтобы были цифры, чекаем чтобы не было лишних категорий, чекаем чтобы в мапинге первым элементов была цифра
        if 'goldapple.ru' in i and '-' in i and has_numbers(i)== True and len(i.split('/')) ==4 and i.split('/')[3][0].isdigit() == True:
            filtered_parsed_list.append(i)

    response = requests.get('https://goldapple.ru/pub/sitemap-1-2.xml')
    parsed_xml_list = response.text.replace('</loc>', '<loc>').split('<loc>')

    for i in parsed_xml_list:
        if 'goldapple.ru' in i and '-' in i and has_numbers(i)== True and len(i.split('/')) ==4 and i.split('/')[3][0].isdigit() == True:
            filtered_parsed_list.append(i)

    len(filtered_parsed_list)

    target_sku_list = []
    for iter_filtered_parsed_list in filtered_parsed_list:
        target_sku_list.append(iter_filtered_parsed_list.split('/')[-1].split('-')[0])

    target_sku_list = list(set(target_sku_list))

    # парсер на всех
    warnings.filterwarnings('ignore')

    logging.basicConfig(filename=logs_global_address, filemode='a+', level=logging.INFO)
    logger = logging.getLogger()

    all_products_from_list = []
    acquired_sku_s = []
    z = 0

    for target_sku in target_sku_list:
        try:
            if target_sku not in acquired_sku_s: # пробую убрать лишние запросы, но так как нет прямого таргета на предмет -
                # идея такого фильтра довольно сомнительна, лучше идей у меня пока нету

                response_api = requests.get('https://goldapple.ru/web_scripts/discover/multiplacement_pdp?placement=item_page.rr1|item_page.rr2|item_page.rr3&purpose=products_slider&sku=%s'%target_sku)

                CasesJson = json.loads(response_api.text)

                # таргет на несколько, но только по одной странице
                try:
                    for itered_key in list(CasesJson.keys()):
                        for product_id in range(0, len(CasesJson[itered_key]['products'])):

                            cases_dict = CasesJson[itered_key]['products'][product_id]
                            cases_dict

                            your_keys = ['id', 'sku', 'name', 'brand', 'brand_type', 'dimension17', 'dimension18', 'dimension19', 'dimension20', 'country',
                                         'price', 'old_price', 'category_type', 'url', 'is_saleable']
                            temp_product_dict = { your_key: cases_dict[your_key] for your_key in your_keys }

                            if temp_product_dict['sku'] not in acquired_sku_s:
                                all_products_from_list.append(temp_product_dict)
                                acquired_sku_s.append(temp_product_dict['sku'])
                except:
                    z+=1
                    #print("trouble with sku: {%s}", target_sku, z) # потом вернуть норм логгер и запускать как просто скрипт
                    logger.info("trouble with sku: {%s}", (target_sku, z))
        except Exception as e:
            logger.info("gold_apple failed: {%s}", (str(e)))
            if 'HTTPSConnectionPool' not in str(e):
                stop
            time.sleep(60)


    today = date.today()

    with open(path_to_db_global+'/data_gold_apple_'+str(today)+'.json', 'w', encoding='utf-8') as f:
        json.dump(all_products_from_list, f, ensure_ascii=False, indent=4)

    now = datetime.now()
    logger.info("gold_apple done, going to database: {%s}", now)
    db_handler.handle_goldapple(str(today))

def parser_iledebeaute():
    #
    import requests
    import json
    import pandas as pd
    from bs4 import BeautifulSoup
    import time
    import re
    from datetime import datetime
    from datetime import date
    import logging

    logging.basicConfig(filename=logs_global_address, filemode='a+', level=logging.INFO)
    logger = logging.getLogger()

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



    based_url = 'https://iledebeaute.ru'

    # список всех брендов

    headers = {
        'Content-Type': 'application/json',
    }

    response = requests.get('https://iledebeaute.ru/files/sitemaps/https/sitemap2.xml')

    parsed_xml_list = response.text.replace('</loc>', '<loc>').split('<loc>')
    filtered_parsed_list = []

    for i in parsed_xml_list:
        if 'iledebeaute.ru' in i:
            filtered_parsed_list.append(i)


    iter_brand_urls = filtered_parsed_list[0]
    response = requests.get(iter_brand_urls)
    print(iter_brand_urls)

    soup = BeautifulSoup(response.text, 'lxml')

    soup.find_all(class_="_js-btn-pagination-more")[0].get('data-next-page-url')

    parsed_iledebeaute_data = []
    prev_number = 0

    for iter_brand_urls in log_progress(filtered_parsed_list):
        try: # проверка чтобы не было отсоединений
            pars_checker = 2
            while True:
                if pars_checker == 2:
                    #парсинг первой страницы
                    # уровень итерации по брендам
                    response = requests.get(iter_brand_urls)
                    #print('first level:', iter_brand_urls)
                    logger.info("first level: {%s}", iter_brand_urls)

                    soup = BeautifulSoup(response.text, 'lxml')
                    pars_checker = 1

                if pars_checker == 0:
                    #парсинг некст страницы
                    # уровень итерации по брендам
                    response = requests.get(based_url + url_part_for_next)
                    #print('next level:', based_url + url_part_for_next)
                    logger.info("next level: {%s}", based_url + url_part_for_next)

                    soup = BeautifulSoup(response.text, 'lxml')
                    pars_checker = 1

                if pars_checker == 1:
                    # обработка страницы бренда
                    # только если произошла загрузка новой страницы
                    for iter_product_id in range(0, len(soup.find_all(class_="b-product-list__item"))):
                        temp_product_dict = {}

                        # айди
                        product_id = soup.find_all(class_="b-product-list__item")[iter_product_id].find_all(class_="b-product-thumb__image")[0].get('data-product-id')

                        # название
                        product_name = soup.find_all(class_="b-product-list__item")[iter_product_id].find_all(class_="b-product-thumb__image")[0].find_all('img')[0].get('alt')

                        # бренд
                        product_brand = soup.find_all(class_="b-product-list__item")[iter_product_id].find_all(class_="b-product-thumb__title")[0].find_all('a')[0].text

                        # ссылка
                        product_url = based_url+ soup.find_all(class_="b-product-list__item")[iter_product_id].find_all(class_="b-product-thumb__short-description")[0].find_all('a')[0].get('href')

                        # цена продукта
                        temp_find_price = soup.find_all(class_="b-product-list__item")[iter_product_id].find_all(class_="b-product-thumb__price-current")[0].text
                        product_price = float(''.join(list(map(str, re.findall(r'\d', temp_find_price)))))

                        try:
                            # комментарий по продукту
                            product_comment = soup.find_all(class_="b-product-list__item")[iter_product_id].find_all(class_="b-product-thumb__custom-field")[0].text.replace('  ','').replace('\n','').replace('\t','')
                        except:
                            product_comment = ''


                        temp_product_dict['product_id'] = product_id
                        temp_product_dict['product_name'] = product_name
                        temp_product_dict['product_brand'] = product_brand
                        temp_product_dict['product_url'] = product_url
                        temp_product_dict['product_price'] = product_price
                        temp_product_dict['product_comment'] = product_comment

                        parsed_iledebeaute_data.append(temp_product_dict)
                    #print('parsed_iledebeaute_data len:', len(parsed_iledebeaute_data))
                    logger.info("parsed_iledebeaute_data len: {%s}", len(parsed_iledebeaute_data))

                try:
                    # проверка на наличие некст страницы
                    url_part_for_next = soup.find_all(class_="_js-btn-pagination-more")[0].get('data-next-page-url')
                    #print('url_part_for_next:', url_part_for_next)
                    pars_checker = 0
                    time.sleep(1)
                except Exception as e:
                    if 'list index out of range' not in str(e):
                        # предотвращение загрузки следующей страницы, все данные бренда получены, последняя страница достигнута
                        stop
                    got_data_number = len(parsed_iledebeaute_data) - prev_number
                    prev_number = len(parsed_iledebeaute_data)
                    #print('got data:', got_data_number)
                    logger.info("got data: {%s}", got_data_number)
                    pars_checker = 2
                    time.sleep(1)
                    #print(e)
                    break

        except Exception as e:
            logger.info("iledebeaute failed: {%s}", (str(e)))
            if 'HTTPSConnectionPool' not in str(e):
                stop
            time.sleep(60)


    today = date.today()

    with open(path_to_db_global+'/data_iledebeaute_'+str(today)+'.json', 'w', encoding='utf-8') as f:
        json.dump(parsed_iledebeaute_data, f, ensure_ascii=False, indent=4)

    now = datetime.now()
    logger.info("iledebeaute done, going to database: {%s}", now)

    db_handler.handle_iledebeaute(str(today))

def parser_letu():

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

    with open(list_of_proxies_global_address, 'rb') as fp:
        list_of_proxies = json.load(fp)

    logging.basicConfig(filename=logs_global_address, filemode='a+', level=logging.INFO)
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

    # эту тему надо тоже будет на автопроверку закинуть
    prev_sku_exists_check = False

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
                        with open(list_of_proxies_global_address, 'rb') as fp:
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
                        with open(list_of_proxies_global_address, 'rb') as fp:
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

                with open(list_of_proxies_global_address, 'rb') as fp:
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

    with open(path_to_db_global+'/data_letu_'+str(today)+'.json', 'w', encoding='utf-8') as f:
        json.dump(all_products_from_list, f, ensure_ascii=False, indent=4)

    now = datetime.now()
    logger.info("letu done, going to database: {%s}", now)

    db_handler.handle_letu(str(today))

def parser_podrygka():
    #
    import requests
    import json
    import pandas as pd
    from bs4 import BeautifulSoup
    import time
    import re
    from datetime import datetime
    from datetime import date
    import logging


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

    logging.basicConfig(filename=logs_global_address, filemode='a+', level=logging.INFO)
    logger = logging.getLogger()

    based_url = ' https://www.podrygka.ru'

    # список всех брендов

    headers = {
        'Content-Type': 'application/json',
    }

    response = requests.get('https://www.podrygka.ru/sitemap_brands.xml')

    parsed_xml_list = response.text.replace('</loc>', '<loc>').split('<loc>')
    filtered_parsed_list = []

    for i in parsed_xml_list:
        if 'podrygka.ru' in i:
            filtered_parsed_list.append(i)

    len(filtered_parsed_list)

    iter_brand_urls = filtered_parsed_list[0]
    response = requests.get(iter_brand_urls)
    print(iter_brand_urls)

    soup = BeautifulSoup(response.text, 'lxml')

    soup.find_all(class_="pagination__button pagination__button--right")[0].get('href')

    parsed_podrygka_data = []
    prev_number = 0
    xxx = ['', '']

    for iter_brand_urls in log_progress(filtered_parsed_list):
        try:
            pars_checker = 2
            while True:
                if pars_checker == 2:
                    #парсинг первой страницы
                    # уровень итерации по брендам
                    response = requests.get(iter_brand_urls)
                    print('first level:', iter_brand_urls)
                    #logger.info("first level: {%s}", iter_brand_urls)

                    soup = BeautifulSoup(response.text, 'lxml')
                    pars_checker = 1

                if pars_checker == 0:
                    #парсинг некст страницы
                    # уровень итерации по брендам
                    response = requests.get(based_url + url_part_for_next)
                    print('next level:', based_url + url_part_for_next)
                    #logger.info("next level: {%s}", based_url + url_part_for_next)

                    soup = BeautifulSoup(response.text, 'lxml')
                    pars_checker = 1

                if pars_checker == 1:
                    # обработка страницы бренда
                    # только если произошла загрузка новой страницы
                    for iter_product_id in range(0, len(soup.find_all(class_="item-product-card"))):
                        temp_product_dict = {}

                        # айди
                        product_id = soup.find_all(class_="item-product-card")[iter_product_id].find_all(class_="products-list-item vertically_sides_in_box")[0].get('data-article')

                        # название
                        product_name = soup.find_all(class_="item-product-card")[iter_product_id].find_all(class_="products-list-item__title")[0].text

                        # бренд
                        product_brand = soup.find_all(class_="item-product-card")[iter_product_id].find_all(class_="brand")[0].text

                        # ссылка
                        product_url = based_url+ soup.find_all(class_="item-product-card")[iter_product_id].find_all(class_="products-list-item__title")[0].get('href')

                        # цена продукта
                        temp_find_price = soup.find_all(class_="item-product-card")[iter_product_id].find_all(class_="price")[0].text
                        product_price = float(temp_find_price)

                        try:
                            # комментарий по продукту (категория)
                            product_comment = soup.find_all(class_="item-product-card")[iter_product_id].find_all(class_="category")[0].text
                        except:
                            product_comment = ''


                        temp_product_dict['product_id'] = product_id
                        temp_product_dict['product_name'] = product_name
                        temp_product_dict['product_brand'] = product_brand
                        temp_product_dict['product_url'] = product_url
                        temp_product_dict['product_price'] = product_price
                        temp_product_dict['product_comment'] = product_comment

                        parsed_podrygka_data.append(temp_product_dict)
                    print('parsed_podrygka_data len:', len(parsed_podrygka_data))
                    #logger.info("parsed_podrygka_data len: {%s}", len(parsed_podrygka_data))

                try:
                    # проверка на наличие некст страницы
                    url_part_for_next = soup.find_all(class_="pagination__button pagination__button--right")[0].get('href')
                    #print('url_part_for_next:', url_part_for_next)
                    if url_part_for_next == None:
                        xxx[5] # вызываем индекс аут оф рейндж
                    pars_checker = 0
                    # попробуем без таймера между страничками
                    #time.sleep(1)
                except Exception as e:
                    if 'list index out of range' not in str(e):
                        # предотвращение загрузки следующей страницы, все данные бренда получены, последняя страница достигнута
                        stop
                    got_data_number = len(parsed_podrygka_data) - prev_number
                    prev_number = len(parsed_podrygka_data)
                    print('got data:', got_data_number)
                    #logger.info("got data: {%s}", got_data_number)
                    pars_checker = 2
                    time.sleep(1)
                    #print(e)
                    break

        except Exception as e:
            logger.info("podrygka failed: {%s}", (str(e)))
            if 'HTTPSConnectionPool' not in str(e):
                stop
            time.sleep(60)


    today = date.today()

    with open(path_to_db_global+'/data_podrygka_'+str(today)+'.json', 'w', encoding='utf-8') as f:
        json.dump(parsed_podrygka_data, f, ensure_ascii=False, indent=4)

    now = datetime.now()
    logger.info("podrygka done, going to database: {%s}", now)

    db_handler.handle_podrygka(str(today))

def parser_rivegauche():
    #
    import requests
    import json
    import pandas as pd
    import time
    from datetime import datetime
    from datetime import date
    import logging

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

    logging.basicConfig(filename=logs_global_address, filemode='a+', level=logging.INFO)
    logger = logging.getLogger()

    headers = {
        'Content-Type': 'application/json',
    }

    response = requests.get('https://rivegauche.ru/sitemap2.xml')

    response

    parsed_xml_list = response.text.replace('</loc>', '<loc>').split('<loc>')
    filtered_parsed_list = []

    for i in parsed_xml_list:
        # чекаем чтобы был дефис, чекаем чтобы были цифры, чекаем чтобы не было лишних категорий, чекаем чтобы в мапинге первым элементов была цифра
        if 'rivegauche.ru' in i:
            filtered_parsed_list.append(i)

    len(filtered_parsed_list)

    filtered_parsed_list[0:50] # нужно убрать в конце цифру если она двух или трехзначная

    filtered_parsed_list_with_no_weights = []
    for i in filtered_parsed_list:
        if i.split('-')[-1].isdigit() == True:
            filtered_parsed_list_with_no_weights.append( i.replace('-'+str(i.split('-')[-1]),'') )

    filtered_parsed_list = list(set(filtered_parsed_list_with_no_weights))

    # получаем бренды

    headers = {
        'Content-Type': 'application/json',
    }

    response = requests.get('https://api.rivegauche.ru/rg/v1/newRG/brands')

    response

    brands_json = json.loads(response.text)

    len(brands_json)

    # делаем каталог айди брендов

    all_brands_id_catalog = []

    for i in brands_json:
        all_brands_id_catalog.append(i['code'])

    #all_brands_id_catalog

    # сразу пишем финальный парсер
    # попробую прямую итерацию без проксей

    # важный момент - сделать отлавливание ошибок и трай-эксепт
    # при первом прогоне ошибок парсинга не обнаружено, прогон успешен

    all_products_from_list = []
    acquired_sku_s = []

    # в данном случае я не уверен в финальном списке товаров,
    # так что логгинг прогресса идет через бренды

    # выше описан план, в дальнейшем можно написать скрипт сверки с сайтмапом
    # и в процентах по url учитывать его заполнение.
    # А так - можно просто сравнить длину полученных данных
    # с колвом записей из сайтмапа

    for iter_brand_id in log_progress(all_brands_id_catalog):
        # итерируем все бренды

        headers = {
        'Content-Type': 'application/json',
        }

        brand_id = iter_brand_id
        current_page = '0'

        response = requests.get('https://api.rivegauche.ru/rg/v1/newRG/products/search?brandCode=%s&currentPage=%s&pageSize=100'% (brand_id, current_page))

        temp_brand_products_json = json.loads(response.text)

        for page_id in range(0, temp_brand_products_json['pagination']['totalPages']):
            # в каждом бренде итерируем по всем его товарам, добавляем их в список
            try:
                if page_id != 0:
                    # прогон нулевой был сделан вне этого цикла
                    headers = {
                    'Content-Type': 'application/json',
                    }

                    brand_id = iter_brand_id
                    current_page = str(page_id)

                    response = requests.get('https://api.rivegauche.ru/rg/v1/newRG/products/search?brandCode=%s&currentPage=%s&pageSize=100'% (brand_id, current_page))

                    temp_brand_products_json = json.loads(response.text)

                for iter_brand_info in temp_brand_products_json['results']:

                    try:
                        iter_brand_info['discountPrice']
                    except Exception as e:
                        if 'discountPrice' not in str(e):
                            print(e)
                            # logger.info("troubles with json: {%s}", e)
                        iter_brand_info['discountPrice'] = iter_brand_info['price']

                    cases_dict = iter_brand_info
                    your_keys = ['code', 'name', 'url','stock', 'availableForPickup', 'manufacturer', 'price', 'volumePricesFlag', 'subtitle', 'prices',
                                 'brand', 'canAddToCart', 'deleted', 'adult', 'discountPrice', 'categoriesChain']
                    temp_product_dict = { your_key: cases_dict[your_key] for your_key in your_keys }

                    if temp_product_dict['code'] not in acquired_sku_s:
                        acquired_sku_s.append(temp_product_dict['code'])
                        all_products_from_list.append(temp_product_dict)
            except Exception as e:
                logger.info("rivegauche failed: {%s}", (str(e)))
                if 'HTTPSConnectionPool' not in str(e):
                    stop
                time.sleep(60)

        # делаем таймаут между брендами
        time.sleep(1)


    today = date.today()

    with open(path_to_db_global+'/data_rivegauche_'+str(today)+'.json', 'w', encoding='utf-8') as f:
        json.dump(all_products_from_list, f, ensure_ascii=False, indent=4)

    now = datetime.now()
    logger.info("rivegauche done, going to database: {%s}", now)

    db_handler.handle_rivegauche(str(today))
