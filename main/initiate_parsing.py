# стартовать раз в неделю по таймеру
# в идеале прикрутить логгинг

# pushd "B:\folder for python files\gitclone\russian_beauty_parser\main"
# python initiate_parsing.py

import runpy
import datetime
from threading import Thread
import logging
import parsers.parsers as parsers
import time


def run_gold_apple(logger_upper):
    #runpy.run_path(path_name='parsers/parser_gold_apple.py')
    now = datetime.datetime.now()
    logger_upper.info("start gold_apple sequence: {%s}", now)

    parsers.parser_gold_apple()

    now = datetime.datetime.now()
    logger_upper.info("gold_apple sequence done: {%s}", now)

def run_iledebeaute(logger_upper):
    #runpy.run_path(path_name='parsers/parser_iledebeaute.py')
    now = datetime.datetime.now()
    logger_upper.info("start iledebeaute sequence: {%s}", now)

    parsers.parser_iledebeaute()

    now = datetime.datetime.now()
    logger_upper.info("iledebeaute sequence done: {%s}", now)

def run_letu(logger_upper):
    #runpy.run_path(path_name='parsers/parser_letu.py')
    now = datetime.datetime.now()
    logger_upper.info("start letu sequence: {%s}", now)

    parsers.parser_letu()

    now = datetime.datetime.now()
    logger_upper.info("letu sequence done: {%s}", now)

def run_podrygka(logger_upper):
    #runpy.run_path(path_name='parsers/parser_podrygka.py')
    now = datetime.datetime.now()
    logger_upper.info("start podrygka sequence: {%s}", now)

    parsers.parser_podrygka()

    now = datetime.datetime.now()
    logger_upper.info("podrygka sequence done: {%s}", now)

def run_rivegauche(logger_upper):
    #runpy.run_path(path_name='parsers/parser_rivegauche.py')
    now = datetime.datetime.now()
    logger_upper.info("start rivegauche sequence: {%s}", now)

    parsers.parser_rivegauche()

    now = datetime.datetime.now()
    logger_upper.info("rivegauche sequence done: {%s}", now)

multithreading_check = False

# while True:

logging.basicConfig(filename='parsers/misc/logs.json', filemode='a+', level=logging.INFO)
logger_upper = logging.getLogger()

# логируем страрт работы парсера
now = datetime.datetime.now()
logger_upper.info("initiating parsing sequence: {%s}", now)

# мультитредовый старт нескольких скриптов одновременно (вообще, их можно сделать как функции и импортировать на старте)
# на некст апдейтах поправлю

if multithreading_check == True:
    thread1 = Thread(target=run_gold_apple, args=(logger_upper,))
    thread2 = Thread(target=run_iledebeaute, args=(logger_upper,))
    thread3 = Thread(target=run_letu, args=(logger_upper,))
    thread4 = Thread(target=run_podrygka, args=(logger_upper,))
    thread5 = Thread(target=run_rivegauche, args=(logger_upper,))

    thread1.start()
    thread2.start()
    thread3.start()
    thread4.start()
    thread5.start()

    thread1.join()
    thread2.join()
    thread3.join()
    thread4.join()
    thread5.join()

elif multithreading_check == False:
    # тут пока можно решеточкой убирать чтобы стартовать с нужного места,
    # а так надо будет проверку на ласт парсинг накинуть
    #run_gold_apple(logger_upper)
    #run_iledebeaute(logger_upper)
    run_letu(logger_upper)
    run_podrygka(logger_upper)
    run_rivegauche(logger_upper)

else:
    print('multithreading_check wtf')

# логируем конец работы парсера
now = datetime.datetime.now()
logger_upper.info("Parsing sequence complete: {%s}", now)

# time.sleep(432000)

# логи потом грузятся в визуализатор и разбираются + лог консоли можно выгружать отдельно и разбирать в моменте
# с визуализацией, и прокидывать алерты если что-то случается
# https://habr.com/ru/company/wunderfund/blog/683880/
# https://qna.habr.com/q/23593 , варики: elasticsearch, Kibana, metabase (на нем можно сделать кастомную систему мониторинга веллбиинг)
