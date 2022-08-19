'''
rtb预估点击率,输入数据格式: label列,数值型特征列,需要label_encode的列
已经是label_encode好的文件
'''
import gflags
import sys


sys.path.append("..")
sys.path.append("../..")
sys.path.append("../../..")
sys.path.append("../../../..")

import evaluate.confusion_matrix_ as cm_

import numpy as np

from utils import logs
from conf.rtb.model import CONFIG as model_config
from conf.rtb.preprocess import CONFIG as preprocess_config

Flags = gflags.FLAGS
gflags.DEFINE_string('log_path', '../../../../logs/xgboost_lr.log', 'log')

# 各种文件路径
gflags.DEFINE_string('in_predict_real_file', "../../../../data/deepfm_product/etl/test.label", 'onehot fit之后的内存文件,保存下来为预估用')  # 通过序列化来做
gflags.DEFINE_string('in_predict_res_file', "../../../../data/deepfm_product/predict/test_res.txt", '预估输出文件')

dic_config = {}

gflags.FLAGS(sys.argv)
logger = logs.Logger(log_path=Flags.log_path).logger


def init():
    global dic_config
    global logger
    dic_config['logger'] = logger
    dic_config['model_config'] = model_config  # xgb训练的参数
    dic_config['preprocess_config'] = preprocess_config  # xgb训练的参数


def run():
    y_test = np.loadtxt(Flags.in_predict_real_file, delimiter=' ')
    y_pred_test = np.loadtxt(Flags.in_predict_res_file, delimiter=' ')
    y_pred_test = np.where(y_pred_test > 0.5, 1, 0)
    cm = cm_.confusion_matrix_(y_test, y_pred_test, np.array([0, 1]))
    cm.compute()


init()
run()

