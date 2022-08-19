'''
rtb预估点击率,输入数据格式: label列,数值型特征列,需要label_encode的列
'''

import gflags
import sys


sys.path.append("..")
sys.path.append("../..")
sys.path.append("../../../..")

from utils import logs

from conf.rtb.model import CONFIG as model_config
from conf.rtb.preprocess import CONFIG as preprocess_config

from train import deepfm

Flags = gflags.FLAGS
gflags.DEFINE_string('log_path', '../../../../logs/xgboost_lr.log', 'log')

# 各种文件路径
gflags.DEFINE_string('in_encode_file', '../../../../data/deepfm/criteo_sampled_data_no_header_encode.csv', '转换后的label_encode文件')

# 保存的model文件
gflags.DEFINE_string('out_model_path', "../../../../data/deepfm/deepfm_model.h5", 'deepfm_model_path')


dic_config = {}

gflags.FLAGS(sys.argv)
logger = logs.Logger(log_path=Flags.log_path).logger


def init():
    global dic_config
    global logger
    dic_config['logger'] = logger
    dic_config['model_config'] = model_config  # xgb训练的参数
    dic_config['preprocess_config'] = preprocess_config  # xgb训练的参数

    dic_config['dev'] = preprocess_config['common']['dev']  # Boolean类型,是否需要拆分

    logger.info(f"=========================开始训练=========================")
    # 输入文件
    dic_config["encode_file_path"] = Flags.in_encode_file  # 原始文件label_encode后的文件

    dic_config["file_separator"] = preprocess_config['common']['file_separator']  # click字段
    dic_config["deepfm_model_path"] = Flags.out_model_path  # deepfm模型文件

    dic_config['need_label_encode_cols_num'] = preprocess_config['common']['need_label_encode_cols_num']  # 需要label_encode字段的个数(在每行的最后)


def train():

    logger.info("""
        ##################################
        ##### DEEPFM Train START #########
        ##################################
    """)
    deepfm_train = deepfm.DeepFMTrain(dic_config)
    deepfm_train.load_data_and_get_feature_names()
    deepfm_train.train()

    logger.info("""
        ##################################
        ##### DEEPFM Train DONE #########
        ##################################
    """)


def run():
    train()


if __name__ == '__main__':
    init()
    run()
