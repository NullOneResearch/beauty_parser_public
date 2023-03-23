import json
import requests
import time
import logging
import random
from datetime import datetime
import bot_commands


logging.basicConfig(filename='databases/tg_api_logs.json', filemode='a+', level=logging.INFO)
logger = logging.getLogger()

path_to_database = 'databases/log_of_requests_db.json'

def get_new_updates(bot_api):
    # current_dict = {}
    # подтягиваем старые ответы
    # нужны регулярные бекапы походу
    with open(path_to_database, 'rb') as fp:
        current_dict = json.load(fp)

    # получение последней сотни запросов
    json_data = {"timeout": 5}

    response_api = requests.get('https://api.telegram.org/bot'+bot_api+'/getUpdates', json=json_data)

    CasesJson = json.loads(response_api.text)

    return current_dict, CasesJson

def handle_updates(current_dict, CasesJson):
    # обработка списка запросов
    for i in CasesJson['result']:
        # у ключа единый формат
        str_update_id = str(i['update_id'])
        try:
            #print(current_dict[str_update_id]['answered_or_not'])
            if current_dict[str_update_id]['answered_or_not'] == False:
                # доп проверка, добавляем в бд только если у него нет записи
                temp_dict = {}
                temp_dict['chat_id'] = i['message']['chat']['id']
                temp_dict['date_sent'] = i['message']['date']

                temp_dict['username'] = i['message']['chat']['username']
                temp_dict['req_text'] = i['message']['text']
                temp_dict['answered_or_not'] = False

                current_dict[str_update_id] = temp_dict
            else:
                pass
        except Exception as e:
            print(e, i['message']['chat']['username'], str(datetime.now()), '|||', i['message']['text'])

            logger.info("new_message: {%s}", (e, i['message']['chat']['username'], str(datetime.now()), '|||', i['message']['text']))

            temp_dict = {}
            temp_dict['chat_id'] = i['message']['chat']['id']
            temp_dict['date_sent'] = i['message']['date']

            temp_dict['username'] = i['message']['chat']['username']
            temp_dict['req_text'] = i['message']['text']
            temp_dict['answered_or_not'] = False

            current_dict[str_update_id] = temp_dict
            # либо если его вообще не найдено в бд (тут доп проверку на имя ошибки)
    return current_dict

def send_responses(current_dict, bot_api):
    # ответы на неотвеченные

    for iter_current_dict in current_dict:
        if current_dict[iter_current_dict]['answered_or_not'] != True:

            # тут ответ
            req_text = current_dict[iter_current_dict]['req_text']

            answer_data = get_info_from_api_db(req_text)

            json_data = {"chat_id": current_dict[iter_current_dict]['chat_id'], "text": answer_data}

            r = requests.post('https://api.telegram.org/bot'+bot_api+'/sendMessage', json=json_data)
            r.status_code

            current_dict[iter_current_dict]['answered_or_not'] = True

        elif current_dict[iter_current_dict]['answered_or_not'] == True:
            pass

    # сохранение лога
    with open(path_to_database, 'w', encoding='utf-8') as f:
        json.dump(current_dict, f, ensure_ascii=False, indent=4)



# обращения к апишке
def get_info_from_api_db(req_text):
    # http://127.0.0.1:8000/data/get/крем

    local_api_response = requests.get('http://127.0.0.1:8000/data/get/'+req_text)

    try: # тут колво выдачи в длине шаффла
        all_answers_from_api = []
        temp_list = list(range(0, len(json.loads(local_api_response.text))))
        random.shuffle(temp_list)
        for i in temp_list[0:10]: # !!! длину шаффла вынес сюда
            all_answers_from_api.append(json.loads(local_api_response.text)[i])
    except Exception as e:
        print(e)
        all_answers_from_api = {}

    # и красиво оформим ответ
    if len(all_answers_from_api) != 0:
        temp_answer = req_text+': Подходящие ответы:\n'
        for iter_local_api_r in all_answers_from_api:
            temp_answer+='Название: '+str(iter_local_api_r[0])+'\n'
            temp_answer+='Цена: '+str(iter_local_api_r[1])+'\n'
            temp_answer+='Производитель: '+str(iter_local_api_r[2])+'\n'
            temp_answer+='Комментарий: '+str(iter_local_api_r[3])+'\n'
            temp_answer+='Ссылка: '+str(iter_local_api_r[5])+'\n'
            temp_answer+='Дата получения: '+str(iter_local_api_r[6])+'\n'
            temp_answer+='Дистрибьютор: '+str(iter_local_api_r[7])+'\n'
            temp_answer+='__________________________\n'

        answer_data = temp_answer

    else:
        answer_data = req_text+': К сожалению ничего не найдено'

    return answer_data
