import os, sys
import datetime

cwd = os.getcwd()
src = "/".join(cwd.split(os.sep)[:-3])
base_path = "/".join(cwd.split(os.sep)[:-4])
sys.path.append(f"{src}{os.sep}")
sys.path.append(f"{base_path}{os.sep}")


import pandas as pd

from utils import logs
from predict import xgboost_lr_rtb as xgb_lr_rtb_pred
from conf.rtb.model import CONFIG as model_config
from conf.rtb.preprocess import CONFIG as preprocess_config


def time_calculation(func):
    '''
    时间差装饰器
    :param func:
    :return:
    '''
    def new_func(a, b):
        start_time = datetime.datetime.now()
        f = func(a, b)
        end_time = datetime.datetime.now()
        interval = (end_time - start_time).min
        print('运行时间为 %f ms' % interval)
        return f
    return new_func

def process_demo():
    logger = logs.Logger(log_path='../../../../logs/xgboost_lr.log').logger

    dic_config = {
        "xgb_model_path": "../../../../data/xgboost_lr/train/xgb_model.pkl",
        'lr_model_path': "../../../../data/xgboost_lr/train/lr_model.bin",
        "need_label_encode_cols_num": 26,
        "use_model_type": "xgboost_lr",
        "out_label_path": "../../../../data/xgboost_lr/feature/label.out",
        "out_one_hot_encoder_path": "../../../../data/xgboost_lr/feature/one_hot_encoder.label",
        "logger": logger,
        'model_config': model_config,
        'preprocess_config': preprocess_config
    }

    xgbLRPredictEntity = xgb_lr_rtb_pred.XgbLRPredict(dic_config)
    # 预估
    list1 = [0.0, 51, 84.0, 4.0, 3633.0, 26.0, 1.0, 4.0, 8.0, 0.0, 1.0, 0.0, 4.0, 192, 250, 25914, 9279, 8, 1, 4717, 8,
             2, 1369, 2728, 766, 1881, 4, 204, 6007, 4, 174, 150, 3, 37743, 0, 13, 6866, 41, 7274]

    pd_stg_input = pd.DataFrame([list1])
    # res = xgbLRPredictEntity.predict_one_xgb(pd_stg_input)
    res = xgbLRPredictEntity.predict_one_xgb_lr(pd_stg_input)
    print(f"res:{res}")


def process_demo_pressure():
    '''
    压测,看执行时间
    :return:
    '''
    logger = logs.Logger(log_path='../../../../logs/xgboost_lr.log').logger

    dic_config = {
        "xgb_model_path": "../../../../data/xgboost_lr/train/xgb_model.pkl",
        'lr_model_path': "../../../../data/xgboost_lr/train/lr_model.bin",
        "need_label_encode_cols_num": 26,
        "use_model_type": "xgboost_lr",
        "out_label_path": "../../../../data/xgboost_lr/feature/label.out",
        "out_one_hot_encoder_path": "../../../../data/xgboost_lr/feature/one_hot_encoder.label",
        "logger": logger,
        'model_config': model_config,
        'preprocess_config': preprocess_config
    }

    xgbLRPredictEntity = xgb_lr_rtb_pred.XgbLRPredict(dic_config)

    interval1 = 0.0
    interval2 = 0.0

    for i in range(10000):
        time1 = datetime.datetime.now()
        # 预估
        list1 = [0.0, 51, 84.0, 4.0, 3633.0, 26.0, 1.0, 4.0, 8.0, 0.0, 1.0, 0.0, 4.0, 192, 250, 25914, 9279, 8, 1, 4717, 8,
                 2, 1369, 2728, 766, 1881, 4, 204, 6007, 4, 174, 150, 3, 37743, 0, 13, 6866, 41, 7274]

        pd_stg_input = pd.DataFrame([list1])
        time2 = datetime.datetime.now()

        res = xgbLRPredictEntity.predict_one_xgb_lr(pd_stg_input)
        time3 = datetime.datetime.now()
        print(f"res:{res}")
        interval1 += (time3 - time2).min  # 预估用的时间



if __name__ == '__main__':
    process_demo()
