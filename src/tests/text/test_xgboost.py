'''
数据全部为数值型的,最后一列为0开始的分类,逗号分割的文件
'''

import gflags
import sys

from train._xgboost import _xgboost as xgb_train
from predict._xgboost import XGBoost as xgb_predict
from utils import logs

sys.path.append("..")

Flags = gflags.FLAGS
gflags.DEFINE_string('run_type', "train", '是否训练,True为训练,False为预测')

gflags.DEFINE_string('data_path', '../../../data/demo/xgboost/text/training.csv', 'data_path')
gflags.DEFINE_string('model_path', '../../../data/demo/xgboost/text/text.model', 'model_path')

# 如果为预估,预估的文件输入地址,需要有model_path
gflags.DEFINE_string('test_path', '../../../data/demo/xgboost/text/testing2_no_lineno.csv', 'test')
gflags.DEFINE_string('out_path', '../../../data/demo/xgboost/text/out.csv', 'out_path')  # 输出

#####################


gflags.DEFINE_string('stop_words_path', '../../../data/demo/xgboost/text/chineseStopWords.txt', 'stop_words_path')
gflags.DEFINE_string('log_path', '../../../logs/xgboost.log', 'log')

dic_config = {}

gflags.FLAGS(sys.argv)
logger = logs.Logger(log_path=Flags.log_path).logger


def init():
    global dic_config
    global logger
    dic_config['logger'] = logger
    run_type = Flags.run_type
    logger.info(f"=====================文本分类开始:{run_type}=========================")
    dic_config['model_path'] = Flags.model_path  # 模型文件
    dic_config["stop_words_path"] = Flags.stop_words_path

    if run_type == "train":
        dic_config["data_path"] = Flags.data_path
    elif run_type == "predict_one":
        # 需要通过原始文件fit后
        dic_config["data_path"] = Flags.data_path
        # # 预测数据,需要model文件和测试文件
        dic_config["test_path"] = Flags.test_path
        dic_config['out_path'] = Flags.out_path
    elif run_type == "predict_batch":
        dic_config["data_path"] = Flags.data_path
        dic_config["test_path"] = Flags.test_path
        dic_config['out_path'] = Flags.out_path

def train():
    logger.info("""
                ####################################
                ##### XGBoost Text Train START #####
                ####################################
                """)
    logger.info("执行文本训练....")
    xgboost_train = xgb_train(dic_config)
    xgboost_train.text_train()


def predict_one():
    # 预测数据,需要model文件和测试文件
    logger.info("""
            ##########################################
            ##### XGBoost Text Predict_One START #####
            ##########################################
            """)

    xgboost_predict = xgb_predict(dic_config)
    bst = xgboost_predict.load_model()
    xgboost_predict.text_load_and_fit_train_data() # 预估要先执行这个
    while True:
        input_str = input("请输入文章\n")
        if input_str == "exit":
            break
        else:
            try:
                predict_res = xgboost_predict.text_predict_one(input_str, bst)
                for i, pre in enumerate(predict_res):
                    # f.write(str(i + 1))
                    # f.write(',')
                    print(str(int(pre) + 1))
            except:
                print("输入错误...")


def predict_batch():
    xgboost_predict = xgb_predict(dic_config)
    logger.info("加载模型.....")
    xgboost_predict.text_predict_batch()


def run():
    run_type = Flags.run_type
    if run_type == "train":
        train()
    elif run_type == "predict_one":
        predict_one()
    elif run_type == "predict_batch":
        predict_batch()
    else:
        logger.error("不支持的类型...")


if __name__ == '__main__':
    init()
    run()
