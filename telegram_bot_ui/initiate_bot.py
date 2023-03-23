import json
import requests
import time
import logging
from datetime import datetime
import bot_commands

# pushd "B:\folder for python files\gitclone\russian_beauty_parser\telegram_bot_ui"
# python initiate_bot.py

logging.basicConfig(filename='databases/tg_api_logs.json', filemode='a+', level=logging.INFO)
logger = logging.getLogger()

bot_api = ''

# пути к Дб в bot_commands
while True:
    try:
        current_dict, CasesJson = bot_commands.get_new_updates(bot_api)

        current_dict = bot_commands.handle_updates(current_dict, CasesJson)

        # инициируем отправку ответов
        bot_commands.send_responses(current_dict, bot_api)
        time.sleep(10)
    except Exception as e:
        print('ALARM ALARM: ', e)
        logger.info("ALARM ALARM: {%s}", (e, str(datetime.now())))
        time.sleep(10)
        pass
