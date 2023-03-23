import json
import database_operations.sql_db as sql_db_operator
import uvicorn

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000'],
    allow_methods=['*'],
    allow_headers=['*']
)

# можно просто через ссылку передать в апишку, пока вот так, потом еще что-нибудь попробую
@app.get('/data/get/{target}')
async def get_data(target):
    # target_words = await target
    target_words = target

    target_words = str(target_words)

    return sql_db_operator.get_data_from_db(target_words)

if __name__ == '__main__':
    uvicorn.run(app, port=3000, host='localhost')
