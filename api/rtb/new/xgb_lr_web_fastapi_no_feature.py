import pickle

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

import pandas as pd
import joblib
from time import strftime, localtime

dic_config = {
    "predict_cols_num": 9  # 预估的数目
}

xgb_model = None
label_dict = None

# 先在外面定义好列名
df_cols = [i for i in range(1, dic_config['predict_cols_num'] + 1)]

class Item(BaseModel):
    query_body: list = None
    xgb_model_path: str = None
    label_encode_path: str = None

# 打印当前时间
def printTime():
    return strftime("%Y-%m-%d %H:%M:%S", localtime())


def load_model_xgb(xgb_model_path):
    global xgb_model
    print(f"[ {printTime()} ] 加载xgb_model:{xgb_model_path}")
    xgb_model = joblib.load(xgb_model_path)

app = FastAPI()  # 必须实例化该类，启动的时候调用


@app.post("/refresh_model")
async def refresh_model(request_data: Item):
    xgb_model_path = request_data.xgb_model_path
    try:
        load_model_xgb(xgb_model_path)

    except Exception as result:
        return '{"status":201,"message":"%s"}' % result
    else:
        return '{"status":"200"}'


@app.post("/query_predict")
async def query_predict(request_data: Item):
    '''
    必须传json的post接口
    :param request_data:
    :return:
    '''
    try:
        input_list = request_data.query_body
        line_df = pd.DataFrame([input_list], columns=df_cols)
        predict_proba = xgb_model.predict_proba(line_df)
        rate = predict_proba[0, 1]
    except Exception as result:
        print(result)
        return '{"status":201,"message":"%s"}' % result
    else:
        return '{"status":200,"rate":%s}' % rate

if __name__ == '__main__':
    load_model_xgb("xgb_model.pkl")

    uvicorn.run(app=app, port=8080)

