'''
rtb预估点击率,输入数据格式: label列,数值型特征列,需要label_encode的列
已经是label_encode好的文件
'''

import os, sys

cwd = os.getcwd()
src = "/".join(cwd.split(os.sep)[:-3])
base_path = "/".join(cwd.split(os.sep)[:-4])
sys.path.append(f"{src}{os.sep}")
sys.path.append(f"{base_path}{os.sep}")

from predict.xgboost_lr_rtb import XgbLRPredict
from utils import logs
from conf.rtb.model import CONFIG as model_config
from conf.rtb.preprocess import CONFIG as preprocess_config

dic_config = {}

logger = logs.Logger(log_path='../../../../logs/xgboost_lr.log').logger


def init():
    global dic_config
    global logger
    dic_config['logger'] = logger
    dic_config['model_config'] = model_config  # xgb训练的参数
    dic_config['preprocess_config'] = preprocess_config  # xgb训练的参数

    dic_config['dev'] = preprocess_config['common']['dev']  # Boolean类型,是否需要拆分
    dic_config['use_model_type'] = 'xgboost_lr'  # 使用的模型的种类

    # 需要被预估的原始文件的路径,列只包括click往后的字段
    dic_config["predict_input_file_path"] = '../../../../data/xgboost_lr/feature/criteo_sampled_data_no_header_need_predict_encode.csv'
    dic_config['predict_output_file_path'] = '../../../../data/xgboost_lr/predict/criteo_sampled_data_no_header_need_predict_res.csv'

    dic_config["file_separator"] = ","  # 每一行文件分隔符
    dic_config["xgb_model_path"] = "../../../../data/xgboost_lr/train/xgb_model.pkl"
    dic_config['out_one_hot_encoder_path'] = "../../../../data/xgboost_lr/feature/one_hot_encoder.label"
    dic_config['lr_model_path'] = "../../../../data/xgboost_lr/train/lr_model.bin"

    # dic_config['need_label_encode_cols_num'] = 26


# 输入的格式要和训练的格式一样
def predict():
    # 预测数据,需要model文件和测试文件
    logger.info("""
            ##########################################
            ##### XGBoost_LR Predict_Batch START #####
            ##########################################
            """)
    xgb_lr_predict = XgbLRPredict(dic_config)
    xgb_lr_predict.predict_batch_xgb_lr()


def run():
    # 预测数据,需要model文件和测试文件
    predict()


if __name__ == '__main__':
    init()
    run()
