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
from keras.models import load_model
from deepctr.layers import custom_objects

mutex = Lock()


dic_config = {
    "predict_cols_num": 11,  # 预估的数目
}

# 先在外面定义好列名
pred_columns = list(str(i) for i in range(1, dic_config["predict_cols_num"]))

deepfm_model = None


# 打印当前时间
def printTime():
    return strftime("%Y-%m-%d %H:%M:%S", localtime())


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
    global deepfm_model
    try:
        json = request.json
        model_path = json.get("model_path")
        # 肯定需要加载的
        if Path(model_path).is_file():
            deepfm_model = load_model(model_path, custom_objects)
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
    load_model(pwd + sep + "xgb_model.pkl")
    set_detail_path(pwd + sep + "label_detail.json")
    app = Application()
    app.router.add_route('/query_predict', query_predict)
    app.router.add_route('/refresh_model', refresh_model)
    app.router.add_route('/get_label_detail', get_label_detail)
    port = sys.argv[1]
    app.run(port=int(port), worker_num=2)

