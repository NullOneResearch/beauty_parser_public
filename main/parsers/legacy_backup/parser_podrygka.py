import database.database_handler as db_handler
#import parsers.database.database_handler as db_handler
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

logging.basicConfig(filename='misc/logs.json', filemode='a+', level=logging.INFO)
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


today = date.today()

with open('database/json_dumps/data_podrygka_'+str(today)+'.json', 'w', encoding='utf-8') as f:
    json.dump(parsed_podrygka_data, f, ensure_ascii=False, indent=4)

now = datetime.now()
logger.info("podrygka done, going to database: {%s}", now)

db_handler.handle_podrygka(str(today))
