import pickle

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

import pandas as pd
import joblib
from time import strftime, localtime
import numpy as np

dic_config = {
    "predict_cols_num": 9,  # 预估的数目
    "need_label_encode_cols_num": 9,
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


def load_label_encode(label_encode_path):
    global label_dict
    print(f"[ {printTime()} ] 加载label_encode:{label_encode_path}")
    with open(label_encode_path, 'rb') as f:
        label_dict = pickle.load(f)  # 是一个dict,字段映射

    # 默认每个都加上unknown
    for index, label_encoder in label_dict.items():
        if not label_encoder.classes_.__contains__('unknown'):
            label_dict[index].classes_ = np.append(label_encoder.classes_, 'unknown')





app = FastAPI()  # 必须实例化该类，启动的时候调用


@app.post("/refresh_model")
async def refresh_model(request_data: Item):
    label_encode_path = request_data.label_encode_path
    xgb_model_path = request_data.xgb_model_path
    try:
        # 加载label_encode
        load_label_encode(label_encode_path)
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
    input_list = request_data.query_body
    try:
        for index, label_encoder in label_dict.items():
            need_encode_data = input_list[index]
            if need_encode_data not in label_encoder.classes_:
                input_list[index] = int(label_encoder.transform(['unknown'])[0])
            else:
                input_list[index] = int(label_encoder.transform([input_list[index]])[0])

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
    load_label_encode("label.out")

    uvicorn.run(app=app, port=8080)

