import os, sys

cwd = os.getcwd()
src = "/".join(cwd.split(os.sep)[:-3])
base_path = "/".join(cwd.split(os.sep)[:-4])
sys.path.append(f"{src}{os.sep}")
sys.path.append(f"{base_path}{os.sep}")

import ast
import pickle

import pandas as pd

import numpy as np

from utils import logs
from predict import xgboost_lr_rtb as xgb_lr_rtb_pred
from conf.rtb.model import CONFIG as model_config
from conf.rtb.preprocess import CONFIG as preprocess_config


def preprocess_label(input_list_str, dic_config, label_dict):
    '''
    预处理,拆分字段和label_encode
    :param input_list_str:
    :return:
    '''
    input_list = ast.literal_eval(input_list_str)

    if dic_config['need_label_encode_cols_num'] > 0:
        for index, label_encoder in label_dict.items():

            need_encode_data = input_list[index]

            if need_encode_data not in label_encoder.classes_:
                if 'unknown' not in label_encoder.classes_:
                    label_encoder.classes_ = np.append(label_encoder.classes_, 'unknown')
                input_list[index] = int(label_encoder.transform(pd.DataFrame([['unknown']]))[0])
            else:
                input_list[index] = int(label_encoder.transform([input_list[index]])[0])
    pd_stg_input = pd.DataFrame([input_list])
    return pd_stg_input


def process_demo():
    logger = logs.Logger(log_path='../../../../logs/xgboost_lr.log').logger

    dic_config = {
        "xgb_model_path": "../../../../data/xgboost/train/xgb_model.pkl",
        "need_label_encode_cols_num": 26,
        "use_model_type": "xgboost",
        "out_label_path": "../../../../data/deepfm/feature/label.out",
        "logger": logger,
        'model_config': model_config,
        'preprocess_config': preprocess_config
    }

    xgbLRPredictEntity = xgb_lr_rtb_pred.XgbLRPredict(dic_config)

    with open(dic_config['out_label_path'], 'rb') as f:
        label_dict = pickle.load(f)

    # 输入,字符串形式的
    input_list_str = '[ 11.1, 1, 5.0, 0.0, 1382.0, 4.0, 15.0, 2.0, 181.0, 1.0, 2.0, 0, 2.0, "68fd1e641", "80e26c9b", "fb936136", "7b4723c4", "25c83c98", "7e0ccccf", "de7995b8", "1f89b562", "a73ee510", "a8cd5504", "b2cb9c98", "37c9c164", "2824a5f6", "1adce6ef", "8ba8b39a", "891b62e7", "e5ba7672", "f54016b9", "21ddcdc9", "b1252a9d", "07b5194c", "-1", "3a171ecb", "c5c50484", "e8b83407", "9727dd16" ]'
    # 预处理
    pd_stg_input = preprocess_label(input_list_str, dic_config, label_dict)
    # 预估
    res = xgbLRPredictEntity.predict_one_xgb(pd_stg_input)
    print(f"res:{res}")


if __name__ == '__main__':
    process_demo()
