import pickle

from japronto import Application

import pandas as pd
import joblib
from pathlib import Path
from time import strftime, localtime
import numpy as np
import sys, os

dic_config = {
    "predict_cols_num": 9,  # 预估的数目
    "need_label_encode_cols_num": 9,
    "use_model_type": "xgboost"
}

xgb_model = None
xgb_lr_model = None
label_dict = None
one_hot_encoder = None

# 先在外面定义好列名
df_cols = [i for i in range(1, dic_config['predict_cols_num'] + 1)]


# 打印当前时间
def printTime():
    return strftime("%Y-%m-%d %H:%M:%S", localtime())


def load_model_xgb(xgb_model_path):
    global xgb_model
    print(f"[ {printTime()} ] 加载xgb_model:{xgb_model_path}")
    xgb_model = joblib.load(xgb_model_path)


def load_model_xgb_lr(xgb_lr_model_path):
    global xgb_lr_model
    print(f"[ {printTime()} ] 加载lr_model:{xgb_lr_model_path}")
    xgb_lr_model = joblib.load(xgb_lr_model_path)


def load_label_encode(label_encode_path):
    global label_dict
    print(f"[ {printTime()} ] 加载label_encode:{label_encode_path}")
    with open(label_encode_path, 'rb') as f:
        label_dict = pickle.load(f)  # 是一个dict,字段映射

    # 默认每个都加上unknown
    for index, label_encoder in label_dict.items():
        if not label_encoder.classes_.__contains__('unknown'):
            label_dict[index].classes_ = np.append(label_encoder.classes_, 'unknown')


def load_one_hot_encode(one_hot_encode_path):
    global one_hot_encoder
    print(f"[ {printTime()} ] one_hot_encode:{one_hot_encode_path}")
    with open(one_hot_encode_path, 'rb') as f:
        one_hot_encoder = pickle.load(f)  # 是一个dict,字段映射


def query_predict(request):
    global label_dict
    try:
        input_list = request.json
        if dic_config['need_label_encode_cols_num'] > 0:
            for index, label_encoder in label_dict.items():
                need_encode_data = input_list[index]
                if need_encode_data not in label_encoder.classes_:
                    input_list[index] = int(label_encoder.transform(['unknown'])[0])
                else:
                    input_list[index] = int(label_encoder.transform([input_list[index]])[0])

        line_df = pd.DataFrame([input_list], columns=df_cols)
        # print(line_df)
        if dic_config['use_model_type'] == "xgboost_lr":
            x_test_leaves = xgb_model.apply(line_df)
            x_test_lr = one_hot_encoder.transform(x_test_leaves).toarray()
            predict_proba = xgb_lr_model.predict_proba(x_test_lr)
        else:
            predict_proba = xgb_model.predict_proba(line_df)

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
        xgb_lr_model_path = json.get("xgb_lr_model_path")
        label_encode_path = json.get("label_encode_path")
        one_hot_encode_path = json.get("one_hot_encode_path")

        if dic_config['need_label_encode_cols_num'] > 0:
            # 如果需要
            load_label_encode(label_encode_path)

        # 肯定需要加载的
        if Path(xgb_model_path).is_file():
            load_model_xgb(xgb_model_path)
        else:
            print(f"[ {printTime()} ] model_path文件不存在:{xgb_model_path}")
            raise NameError(f"[ {printTime()} ] model_path文件不存在:{xgb_model_path}")

        if dic_config['use_model_type'] == "xgboost_lr":
            # 是最复杂的xgb+lr
            if Path(xgb_lr_model_path).is_file():
                load_model_xgb_lr(xgb_lr_model_path)
            else:
                print(f"[ {printTime()} ] xgb_lr_model_path 文件不存在:{xgb_lr_model_path}")
                raise NameError(f"[ {printTime()} ] xgb_lr_model_path 文件不存在:{xgb_lr_model_path}")

            if Path(one_hot_encode_path).is_file():
                load_one_hot_encode(one_hot_encode_path)
            else:
                print(f"[ {printTime()} ] one_hot_encode_path 文件不存在:{one_hot_encode_path}")
                raise NameError(f"[ {printTime()} ] one_hot_encode_path 文件不存在:{one_hot_encode_path}")

    except Exception as result:
        return request.Response(text='{"status":201,"message":"%s"}' % result)
    else:
        return request.Response(text='{"status":"200"}')


if __name__ == '__main__':
    pwd = os.getcwd()
    sep = os.sep
    # 初始化,肯定要加载这个
    load_model_xgb(pwd + sep + "xgb_model.pkl")

    if dic_config['need_label_encode_cols_num'] > 0:
        load_label_encode(pwd + sep + "label.out")

    if dic_config['use_model_type'] == "xgboost_lr":
        load_model_xgb_lr(pwd + sep + "lr_model.pkl")
        load_one_hot_encode(pwd + sep + "one_hot.out")

    app = Application()
    app.router.add_route('/query_predict', query_predict)
    app.router.add_route('/refresh_model', refresh_model)
    app.run(port=8085, worker_num=2)
