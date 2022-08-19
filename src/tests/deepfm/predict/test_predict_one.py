import ast
import sys, os

cwd = os.getcwd()
src = "/".join(cwd.split(os.sep)[:-3])
base_path = "/".join(cwd.split(os.sep)[:-4])
sys.path.append(f"{src}{os.sep}")
sys.path.append(f"{base_path}{os.sep}")

from predict import deepfm as predict_deepfm
from conf.rtb.model import CONFIG as model_config
from conf.rtb.preprocess import CONFIG as preprocess_config

import pandas as pd

import pickle

import joblib
import numpy as np

# 预处理文件
def preprocess_label(dic_config, input_list_str, dense_cols_num, pred_columns):
    input_list = ast.literal_eval(input_list_str)

    # 处理sparse_feature
    if dic_config['need_label_encode_cols_num'] > 0:
        # label_encode需要
        with open(dic_config['out_label_path'], 'rb') as f:
            label_dict = pickle.load(f)

        for index, label_encoder in label_dict.items():
            need_encode_data = input_list[index]

            if need_encode_data not in label_encoder.classes_:
                if 'unknown' not in label_encoder.classes_:
                    label_encoder.classes_ = np.append(label_encoder.classes_, 'unknown')
                input_list[index] = int(label_encoder.transform(pd.DataFrame([['unknown']]))[0])
            else:
                input_list[index] = int(label_encoder.transform([input_list[index]])[0])

    # dense_feature处理
    if dic_config['dense_feature_type'] == "minmaxscaler" and len(dic_config['select_cols']) - 1 != dic_config['need_label_encode_cols_num']:
        mms = joblib.load(dic_config['mms_save_file'])
        ndarray1 = np.array([input_list[:dense_cols_num]])  # 找到数字列
        df_mms = mms.transform(ndarray1)
        pd_stg_input = pd.concat([pd.DataFrame(df_mms), pd.DataFrame([input_list[dense_cols_num: -1]])], axis=1)
    elif dic_config['dense_feature_type'] == "log":
        for i in range(0, dense_cols_num):
            if input_list[i] > -1:
                input_list[i] = np.log(input_list[i] + 1)
            else:
                input_list[i] = -1
        pd_stg_input = pd.DataFrame([input_list])
    else:  # none
        pd_stg_input = pd.DataFrame([input_list])
        # 上面准备完成后开始预测前

    pd_stg_input.columns = pred_columns
    return pd_stg_input


def process_demo():
    dic_config = {
        'preprocess_config': preprocess_config,
        "model_config": model_config,
        "file_separator": ",",
        "logger": 1,
        "split_cols_file_path": "../../../../data/preprocess/deepfm/preprocess/criteo_sampled_data_no_header_need_predict_split.csv",
        "encode_file_path": "../../../../data/deepfm/feature/criteo_sampled_data_no_header_need_predict_split_encode.csv",
        "out_label_path": "../../../../data/deepfm/feature/label.out",
        "out_label_detail_path": "../../../../data/deepfm/feature/label_detail.json",
        "predict_input_file_path": '../../../../data/deepfm/feature/criteo_sampled_data_no_header_need_predict_encode.csv',
        "need_label_encode_cols_num": 26,
        "select_cols": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
                        21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39],
        "deepfm_model_path": '../../../../data/deepfm/train/deepfm_model.h5',
        "predict_output_file_path": "../../../../data/deepfm/predit/criteo_sampled_data_no_header_pred_res.txt",
        "dense_feature_type": 'log',  # log / minmaxscaler
        "mms_save_file": "../../../../data/deepfm/feature/mms.save",
    }



    # 预测用
    pred_columns = list(str(i) for i in range(1, len(dic_config['select_cols'])))
    # 数值型的字段的长度
    dense_cols_num = len(dic_config["select_cols"]) - dic_config['need_label_encode_cols_num'] - 1

    # 输入
    input_list_str = '[ 11.1, 1, 5.0, 0.0, 1382.0, 4.0, 15.0, 2.0, 181.0, 1.0, 2.0, 0, 2.0, "68fd1e64", "80e26c9b", "fb936136", "7b4723c4", "25c83c98", "7e0ccccf", "de7995b8", "1f89b562", "a73ee510", "a8cd5504", "b2cb9c98", "37c9c164", "2824a5f6", "1adce6ef", "8ba8b39a", "891b62e7", "e5ba7672", "f54016b9", "21ddcdc9", "b1252a9d", "07b5194c", "-1", "3a171ecb", "c5c50484", "e8b83407", "9727dd16" ]'
    # 预处理
    pd_stg_input = preprocess_label(dic_config, input_list_str, dense_cols_num, pred_columns)
    # 预估
    deepfm_predict = predict_deepfm.DeepFmPredict(dic_config)
    res = deepfm_predict.predict_one(pd_stg_input)
    print(res)


def process_product():
    dic_config = {
        'preprocess_config': preprocess_config,
        "model_config": model_config,
        "file_separator": ",",
        "logger": 1,
        "split_cols_file_path": "../../../../data/preprocess/deepfm_product/preprocess/test.txt",
        "out_label_path": "../../../../data/deepfm_product/feature/label.out",
        "out_label_detail_path": "../../../../data/deepfm_product/feature/label_detail.json",
        "predict_input_file_path": "../../../../data/deepfm_product/feature/test_encode.txt",
        "need_label_encode_cols_num": 11,
        "select_cols": [0, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
        "deepfm_model_path": '../../../../data/deepfm_product/train/deepfm_model.h5',
        "predict_output_file_path": "../../../../data/deepfm_product/predit/criteo_sampled_data_no_header_pred_res.txt",
        "dense_feature_type": 'minmaxscaler',  # log / minmaxscaler
        "mms_save_file": "../../../../data/deepfm_product/feature/mms.save",
    }



    # 预测用
    pred_columns = list(str(i) for i in range(1, len(dic_config['select_cols'])))
    # 数值型的字段的长度
    dense_cols_num = len(dic_config["select_cols"]) - dic_config['need_label_encode_cols_num'] - 1

    # 输入,没有拆分,直接全部特征
    input_list_str = "['0','30788','25507','290','3','1','18','OPPO','PBAM00','unknown','me.toutiaoapp']"
    # 预处理
    pd_stg_input = preprocess_label(dic_config, input_list_str, dense_cols_num, pred_columns)
    # 预估
    deepfm_predict = predict_deepfm.DeepFmPredict(dic_config)
    res = deepfm_predict.predict_one(pd_stg_input)
    print(res)



if __name__ == '__main__':
    # process_demo()
    process_product()
