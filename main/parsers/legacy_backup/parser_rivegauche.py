import database.database_handler as db_handler
#import parsers.database.database_handler as db_handler
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

logging.basicConfig(filename='misc/logs.json', filemode='a+', level=logging.INFO)
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

    # делаем таймаут между брендами
    time.sleep(1)


today = date.today()

with open('database/json_dumps/data_rivegauche_'+str(today)+'.json', 'w', encoding='utf-8') as f:
    json.dump(all_products_from_list, f, ensure_ascii=False, indent=4)

now = datetime.now()
logger.info("rivegauche done, going to database: {%s}", now)

db_handler.handle_rivegauche(str(today))
