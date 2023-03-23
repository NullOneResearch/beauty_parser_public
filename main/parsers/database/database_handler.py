import sqlite3
import json
import pandas as pd
from datetime import date
import logging

# pushd "B:\folder for python files\gitclone\russian_beauty_parser\fast-api"
# uvicorn main:app --reload

# скрипт с основными функциями для подтягивания и закидывания жсонов

# 'product_name', 'price', 'brand', 'comment', 'inside_code', 'url', 'date_acquired', 'source_seller'

# надо бы вынести эти пути нормально потом
global_handle_json_path = 'parsers/database/json_dumps'
global_path_to_db = 'parsers/database/sql_dbs'

def get_db_and_date():
    logging.basicConfig(filename='logs_db.json', filemode='a+', level=logging.INFO)
    logger = logging.getLogger()

    con = sqlite3.connect(global_path_to_db+"/russian_beauty_parser.db")

    cur = con.cursor()

    date_acquired = date.today()

    return con, cur, date_acquired, logger

def handle_goldapple(parsed_date):
    con, cur, date_acquired, logger = get_db_and_date()

    # мб сделать пошаговую загрузку для каждого поставщика с трай-эксептом
    with open(global_handle_json_path+'/data_gold_apple_'+str(parsed_date)+'.json', 'rb') as fp:
        parsed_gold_apple_data = json.load(fp)

    insert_gold_apple = []
    for i in parsed_gold_apple_data:
        product_name = i['name']
        price = i['price']
        brand = i['brand']

        comment_info = ''
        for iter_insert in ([i['category_type'], i['dimension17'], i['dimension18'], i['dimension19'], i['dimension20'], i['country']]):
            try:
                comment_info+=iter_insert + ' | '
            except:
                pass

        comment = comment_info
        inside_code = i['sku']
        url = i['url']
        source_seller = 'Золотое яблоко'
        insert_gold_apple.append((product_name, price, brand, comment, inside_code, url, date_acquired, source_seller))

    data = insert_gold_apple

    #if delete_history == True:
        #скрипт для удаления истории и полного обновления, но он целиком сносит
        #cur.execute("DELETE FROM cosmetics WHERE source_seller=?", source_seller)
        #con.commit()

    logger.info("new values added to: {%s}", (source_seller, data))

    cur.executemany("INSERT INTO cosmetics VALUES(?, ?, ?, ?, ?, ?, ?, ?)", data)
    con.commit()
    con.close()


def handle_letu(parsed_date):
    con, cur, date_acquired, logger = get_db_and_date()

    with open(global_handle_json_path+'/data_letu_'+str(parsed_date)+'.json', 'rb') as fp:
        parsed_letu_data = json.load(fp)

    insert_letu = []
    for i in parsed_letu_data:
        product_name = i['displayName']
        price = i['price']
        brand = i['brandName']
        comment = i['categoryName']+' | '+ i['minSkuName']
        inside_code = i['id']
        url = 'https://www.letu.ru' + i['url']
        source_seller = 'Летуаль'
        insert_letu.append((product_name, price, brand, comment, inside_code, url, date_acquired, source_seller))

    data = insert_letu

    #if delete_history == True:
        #скрипт для удаления истории и полного обновления, но он целиком сносит
        #cur.execute("DELETE FROM cosmetics WHERE source_seller=?", source_seller)
        #con.commit()

    logger.info("new values added to: {%s}", (source_seller, data))

    cur.executemany("INSERT INTO cosmetics VALUES(?, ?, ?, ?, ?, ?, ?, ?)", data)
    con.commit()
    con.close()


def handle_rivegauche(parsed_date):
    con, cur, date_acquired, logger = get_db_and_date()

    with open(global_handle_json_path+'/data_rivegauche_'+str(parsed_date)+'.json', 'rb') as fp:
        parsed_rivegauche_data = json.load(fp)

    insert_rivegauche = []
    for i in parsed_rivegauche_data:
        product_name = i['name']
        price = i['price']['value']
        brand = i['manufacturer']
        comment = i['categoriesChain']
        inside_code = i['code']
        url = 'https://rivegauche.ru' + i['url']
        source_seller = 'Ривгош'
        insert_rivegauche.append((product_name, price, brand, comment, inside_code, url, date_acquired, source_seller))

    data = insert_rivegauche

    #if delete_history == True:
        #скрипт для удаления истории и полного обновления, но он целиком сносит
        #cur.execute("DELETE FROM cosmetics WHERE source_seller=?", source_seller)
        #con.commit()

    logger.info("new values added to: {%s}", (source_seller, data))

    cur.executemany("INSERT INTO cosmetics VALUES(?, ?, ?, ?, ?, ?, ?, ?)", data)
    con.commit()
    con.close()


def handle_iledebeaute(parsed_date):
    con, cur, date_acquired, logger = get_db_and_date()

    with open(global_handle_json_path+'/data_iledebeaute_'+str(parsed_date)+'.json', 'rb') as fp:
        parsed_iledebeaute_data = json.load(fp)

    insert_iledebeaute = []
    for i in parsed_iledebeaute_data:
        product_name = i['product_name']
        price = i['product_price']
        brand = i['product_brand']
        comment = i['product_comment']
        inside_code = i['product_id']
        url = i['product_url']
        source_seller = 'Ильдеботе'
        insert_iledebeaute.append((product_name, price, brand, comment, inside_code, url, date_acquired, source_seller))

    data = insert_iledebeaute

    #if delete_history == True:
        #скрипт для удаления истории и полного обновления, но он целиком сносит
        #cur.execute("DELETE FROM cosmetics WHERE source_seller=?", source_seller)
        #con.commit()

    logger.info("new values added to: {%s}", (source_seller, data))

    cur.executemany("INSERT INTO cosmetics VALUES(?, ?, ?, ?, ?, ?, ?, ?)", data)
    con.commit()
    con.close()


def handle_podrygka(parsed_date):
    con, cur, date_acquired, logger = get_db_and_date()

    with open(global_handle_json_path+'/data_podrygka_'+str(parsed_date)+'.json', 'rb') as fp:
        parsed_podrygka_data = json.load(fp)

    insert_podrygka = []
    for i in parsed_podrygka_data:
        product_name = i['product_name']
        price = i['product_price']
        brand = i['product_brand']
        comment = i['product_comment']
        inside_code = i['product_id']
        url = i['product_url']
        source_seller = 'Подружка'
        insert_podrygka.append((product_name, price, brand, comment, inside_code, url, date_acquired, source_seller))

    data = insert_podrygka

    #if delete_history == True:
        #скрипт для удаления истории и полного обновления, но он целиком сносит
        #cur.execute("DELETE FROM cosmetics WHERE source_seller=?", source_seller)
        #con.commit()

    logger.info("new values added to: {%s}", (source_seller, data))

    cur.executemany("INSERT INTO cosmetics VALUES(?, ?, ?, ?, ?, ?, ?, ?)", data)
    con.commit()
    con.close()


####
