import database.database_handler as db_handler
#import parsers.database.database_handler as db_handler
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

logging.basicConfig(filename='misc/logs.json', filemode='a+', level=logging.INFO)
logger = logging.getLogger()

all_products_from_list = []
acquired_sku_s = []
z = 0

for target_sku in target_sku_list:

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


today = date.today()

with open('database/json_dumps/data_gold_apple_'+str(today)+'.json', 'w', encoding='utf-8') as f:
    json.dump(all_products_from_list, f, ensure_ascii=False, indent=4)

now = datetime.now()
logger.info("gold_apple done, going to database: {%s}", now)
db_handler.handle_goldapple(str(today))
