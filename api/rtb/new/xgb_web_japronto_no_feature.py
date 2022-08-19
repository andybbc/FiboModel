import json
import pickle

from japronto import Application

import pandas as pd
import joblib
from pathlib import Path
from time import strftime, localtime
import numpy as np
import sys, os

from threading import Thread, Lock, enumerate

mutex = Lock()


dic_config = {
    "predict_cols_num": 11,  # 预估的数目
}

xgb_model = None

# 明细路径
label_detail_path: str = None

# 先在外面定义好列名
df_cols = [i for i in range(1, dic_config['predict_cols_num'] + 1)]


# 打印当前时间
def printTime():
    return strftime("%Y-%m-%d %H:%M:%S", localtime())


def load_model_xgb(xgb_model_path):
    global xgb_model
    print(f"[ {printTime()} ] 加载xgb_model:{xgb_model_path}")
    xgb_model = joblib.load(xgb_model_path)


def set_detail_path(label_detail_path1):
    global label_detail_path
    label_detail_path = label_detail_path1
    print(f"刷新:{label_detail_path}")


def query_predict(request):
    try:
        input_list = request.json
        line_df = pd.DataFrame([input_list], columns=df_cols)
        # print(line_df)
        mutex.acquire()
        predict_proba = xgb_model.predict_proba(line_df)
        mutex.release()
        rate = predict_proba[0, 1]
    except Exception as result:
        print(result)
        return request.Response(text='{"status":201,"message":"%s"}' % result)
    else:
        return request.Response(text='{"status":200,"rate":%s}' % rate)


def refresh_model(request):
    # print("=" * 10)
    try:
        json = request.json
        xgb_model_path = json.get("xgb_model_path")
        label_detail_path1 = json.get("label_detail_path")
        load_model_xgb(xgb_model_path)
        set_detail_path(label_detail_path1)
    except Exception as result:
        return request.Response(text='{"status":201,"message":"%s"}' % result)
    else:
        return request.Response(text='{"status":"200"}')


def get_label_detail(request):
    try:
        # print("请求label_detail:" + label_detail_path)
        with open(label_detail_path, 'r', encoding='utf-8') as f:
            ret_dic = json.load(f)
            json_str = json.dumps(ret_dic)

    except Exception as result:
        return request.Response(text='{"status":201,"message":"%s"}' % result)
    else:
        return request.Response(text='{"status":200,"json_detail":%s}' % json_str)


if __name__ == '__main__':
    pwd = os.getcwd()
    sep = os.sep
    # 初始化,肯定要加载这个
    load_model_xgb(pwd + sep + "xgb_model.pkl")
    set_detail_path(pwd + sep + "label_detail.json")
    app = Application()
    app.router.add_route('/query_predict', query_predict)
    app.router.add_route('/refresh_model', refresh_model)
    app.router.add_route('/get_label_detail', get_label_detail)
    port = sys.argv[1]
    app.run(port=int(port), worker_num=2)

