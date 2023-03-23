import sqlite3
import json
import pandas as pd
from datetime import date
from datetime import datetime
import logging

# скрипт с функциями обработчика БД
# здесь же будет поисковый алгоритм, нужны доп проверки на соответствия брендам и всему такому
# крч нужны более сложные sql-запросы, пока оставил для теста максимально изичный

# 'product_name', 'price', 'brand', 'comment', 'inside_code', 'url', 'date_acquired', 'source_seller'

def get_db_and_date():
    logging.basicConfig(filename='database_operations/logs_db.json', filemode='a+', level=logging.INFO)
    logger = logging.getLogger()

    path_to_folder = "B:/folder for python files/gitclone/russian_beauty_parser/main/parsers/database/"
    con = sqlite3.connect(path_to_folder+"sql_dbs/russian_beauty_parser.db")

    cur = con.cursor()

    date_acquired = date.today()

    return con, cur, date_acquired, logger

def get_data_from_db(target_words):
    # здесб надо будет прикрутить алгоритм поиска, но пока просто работа со строгим запросом
    con, cur, date_acquired, logger = get_db_and_date()

    product_name = "%"+str(target_words)+"%"
    #product_name = product_name.lower()

    now = datetime.now()
    logger.info("new request: {%s}", (product_name, str(now)))

    #cur.execute("SELECT * FROM cosmetics WHERE product_name like '"+product_name+"' or product_name like '"+product_name+"' or product_name like '"+product_name+"';")

    #cur.execute("SELECT * FROM cosmetics WHERE lower(product_name) like lower(?);", [product_name])
    #cur.execute("SELECT * FROM cosmetics WHERE lower(brand) like lower(?);", [product_name])
    #cur.execute("SELECT * FROM cosmetics WHERE lower(comment) like lower(?);", [product_name])

    cur.execute('''SELECT * FROM cosmetics WHERE
    lower(product_name) like lower(?)
    or lower(brand) like lower(?)
    or lower(comment) like lower(?);''', [product_name, product_name, product_name])

    data = cur.fetchall()
    return data
