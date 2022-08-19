'''
rtb预估点击率,输入数据格式: label列,数值型特征列,需要label_encode的列
'''

import os,sys

cwd = os.getcwd()
src = "/".join(cwd.split(os.sep)[:-3])
base_path = "/".join(cwd.split(os.sep)[:-4])
sys.path.append(f"{src}{os.sep}")
sys.path.append(f"{base_path}{os.sep}")


import train.xgboost_lr_rtb as xgboost_lr_train
from utils import logs
from conf.rtb.model import CONFIG as model_config

dic_config = {}

logger = logs.Logger(log_path='../../../../logs/xgboost_lr.log').logger


def init():
    global dic_config
    global logger
    dic_config['logger'] = logger

    dic_config['dev'] = True  # Boolean类型,是否需要拆分

    dic_config['model_config'] = model_config  # xgb训练的参数
    # 输入文件
    dic_config["encode_file_path"] = '../../../../data/xgboost_lr/feature/criteo_sampled_data_no_header_encode.csv'  # 原始文件label_encode后的文件
    dic_config["train_file_path"] = "../../../../data/xgboost_lr/feature/criteo_sampled_data_no_header_encode_train.csv"
    dic_config["vali_file_path"] = "../../../../data/xgboost_lr/feature/criteo_sampled_data_no_header_encode_vali.csv"
    dic_config["test_file_path"] = "../../../../data/xgboost_lr/feature/criteo_sampled_data_no_header_encode_test.csv"

    dic_config['out_one_hot_encoder_path'] = "../../../../data/xgboost_lr/feature/one_hot_encoder.label"
    dic_config["file_separator"] = ","  # click字段
    dic_config["xgb_model_path"] = "../../../../data/xgboost_lr/train/xgb_model.pkl"  # 模型文件,输出
    dic_config["xgb_pmml_model_path"] = "../../../../data/xgboost_lr/train/xgb_model.pmml"  # pmml模型文件,输出
    dic_config['lr_model_path'] = "../../../../data/xgboost_lr/train/lr_model.bin"
    dic_config['lr_pmml_model_path'] = "../../../../data/xgboost_lr/train/lr_model.pmml"

    dic_config['need_label_encode_cols_num'] = 26  # 需要label_encode字段的个数(在每行的最后)
    dic_config['use_model_type'] = "xgboost_lr"

def train():

    logger.info("""
        ##################################
        ##### XGBoost_LR Train START #####
        ##################################
    """)
    xgb_lr_train = xgboost_lr_train.Xgboost_lr_rtb(dic_config)
    xgb_lr_train.load_data()
    xgb_lr_train.train()

    logger.info("""
        #################################
        ##### XGBoost_RL Train DONE #####
        #################################
    """)


def run():
    train()

if __name__ == '__main__':
    init()
    run()
