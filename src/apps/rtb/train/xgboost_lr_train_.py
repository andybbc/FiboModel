'''
rtb预估点击率,输入数据格式: label列,数值型特征列,需要label_encode的列
'''

import gflags
import sys


sys.path.append("..")
sys.path.append("../..")
sys.path.append("../../../..")

import train.xgboost_lr_rtb as xgboost_lr_train
from utils import logs
from conf.rtb.model import CONFIG as model_config
from conf.rtb.preprocess import CONFIG as preprocess_config

Flags = gflags.FLAGS
gflags.DEFINE_string('log_path', '../../../../logs/xgboost_lr.log', 'log')

# 各种文件路径
gflags.DEFINE_string('in_encode_file', '../../../../data/xgb_lr_demo_new/new_no_request_id/new_sample_encode.csv', '转换后的label_encode文件')
gflags.DEFINE_string('out_one_hot_encoder_path', "../../../../data/xgb_lr_demo_new/new_no_request_id/one_hot.out",
                     'onehot fit之后的内存文件,保存下来为预估用')  # 通过序列化来做

# 拆分文件,只有xgboost可能用到
gflags.DEFINE_string('out_train_file', "../../../../data/xgb_lr_demo_new/new_no_request_id/new_sample_train.csv", 'train_file_path')
gflags.DEFINE_string('out_vali_file', "../../../../data/xgb_lr_demo_new/new_no_request_id/new_sample_vali.csv", 'vali_file_path')
gflags.DEFINE_string('out_test_file', "../../../../data/xgb_lr_demo_new/new_no_request_id/new_sample_test.csv", 'test_file_path')

# 保存的model文件
gflags.DEFINE_string('out_xgb_model_path', "../../../../data/xgb_lr_demo_new/new_no_request_id/xgb_model.pkl", 'xgb_model_path')
gflags.DEFINE_string('out_xgb_pmml_model_path', "../../../../data/xgb_lr_demo_new/new_no_request_id/xgb_model.pmml", 'xgb_pmml_model_path')
gflags.DEFINE_string('out_lr_model_path', "../../../../data/xgb_lr_demo_new/new_no_request_id/lr_model.pkl", 'lr_model_path')
gflags.DEFINE_string('out_lr_pmml_model_path', "../../../../data/xgb_lr_demo_new/new_no_request_id/lr_model.pmml", 'lr_pmml_model_path')


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
    dic_config['use_model_type'] = 'xgboost_lr'  # 使用的模型的种类

    logger.info(f"=========================开始训练=========================")
    # 输入文件
    dic_config["encode_file_path"] = Flags.in_encode_file  # 原始文件label_encode后的文件
    dic_config["out_one_hot_encoder_path"] = Flags.out_one_hot_encoder_path  # map,转换列的数据,label_encode

    ## 训练可能用的到?
    dic_config["train_file_path"] = Flags.out_train_file  # 拆分后训练的数据
    dic_config["vali_file_path"] = Flags.out_vali_file  # 拆分后
    dic_config["test_file_path"] = Flags.out_test_file  # 拆分后

    dic_config["file_separator"] = preprocess_config['common']['file_separator']  # click字段

    dic_config["xgb_model_path"] = Flags.out_xgb_model_path  # 模型文件
    dic_config["xgb_pmml_model_path"] = Flags.out_xgb_pmml_model_path  # pmml模型文件
    dic_config["lr_model_path"] = Flags.out_lr_model_path  # 模型文件
    dic_config["lr_pmml_model_path"] = Flags.out_lr_pmml_model_path  # pmml模型文件

    dic_config['need_label_encode_cols_num'] = preprocess_config['common']['need_label_encode_cols_num']  # 需要label_encode字段的个数(在每行的最后)


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
        ##### XGBoost_LR Train DONE #####
        #################################
    """)


def run():
    train()

if __name__ == '__main__':
    init()
    run()
