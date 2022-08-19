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
gflags.DEFINE_string('run_type', "predict_one", '是否训练,True为训练,False为预测')

gflags.DEFINE_string('data_path', '../../../data/demo/xgboost/seeds_dataset.txt', 'data_path')
gflags.DEFINE_string('model_path', '../../../data/demo/xgboost/seeds.model', 'model_path')

# 如果为预估,预估的文件输入地址,需要有model_path
gflags.DEFINE_string('test_path', '../../../data/demo/xgboost/seeds_dataset_test.txt', 'test')
gflags.DEFINE_string('out_path', '../../../data/demo/xgboost/out.csv', 'out_path')  # 输出

gflags.DEFINE_string('log_path', '../../logs/xgboost.log', 'log')

dic_config = {}

gflags.FLAGS(sys.argv)
logger = logs.Logger(log_path=Flags.log_path).logger


def init():
    global dic_config
    global logger
    dic_config['logger'] = logger
    run_type = Flags.run_type
    logger.info(f"=========================开始:{run_type}=========================")
    dic_config['model_path'] = Flags.model_path  # 模型文件

    # 训练数据,生成model文件,只需要train_path
    if run_type == "train":
        dic_config["data_path"] = Flags.data_path
    elif run_type == "predict_one":
        # # 预测数据,需要model文件和测试文件
        dic_config["test_path"] = Flags.test_path
        dic_config['out_path'] = Flags.out_path
        pass
    elif run_type == "predict_batch":
        # 预测数据,需要model文件和测试文件
        dic_config["test_path"] = Flags.test_path
        dic_config['out_path'] = Flags.out_path
    elif run_type == "k_fold":
        # k_fold_test
        dic_config["data_path"] = Flags.data_path
    else:
        logger.error("不支持的类型")

def train():
    logger.info("""

            ###############################
            ##### XGBoost Train START #####
            ###############################
            """)
    # 计算训练测试数据集
    xgboost_train = xgb_train(dic_config)
    X_train, X_test, y_train, y_test = xgboost_train.load_data()

    xgboost_train.train(X_train, X_test, y_train, y_test)

    logger.info("""
            ###############################
            ##### XGBoost Train DONE #####
            ###############################
            """)


def predict_batch():
    # 预测数据,需要model文件和测试文件
    logger.info("""
            #################################
            ##### XGBoost Predict_Batch START #####
            #################################
            """)

    xgboost_predict = xgb_predict(dic_config)
    logger.info("加载模型.....")
    xgboost_predict.load_model()
    xgboost_predict.predict_batch()


def predict_one():
    # 预测数据,需要model文件和测试文件
    logger.info("""
        #####################################
        ##### XGBoost Predict_One START #####
        #####################################
        """)

    xgboost_predict = xgb_predict(dic_config)
    bst = xgboost_predict.load_model()
    while True:
        input_str = input("请输入特征,用,分割\n")
        if input_str == "exit":
            break
        else:
            try:
                predict_res = xgboost_predict.predict_one(input_str, bst)
                print(predict_res)
            except:
                print("输入错误...")

    logger.info("""
        #################################
        ##### XGBoost Predict DONE #####
        #################################
        """)


def k_fold_test():
    xgboost_train = xgb_train(dic_config)
    xgboost_train.k_fold_test()
    pass


def run():
    run_type = Flags.run_type
    if run_type == "train":
        train()
    elif run_type == "predict_one":
        # 预测数据,需要model文件和测试文件
        predict_one()
    elif run_type == "predict_batch":
        # 预测数据,需要model文件和测试文件
        predict_batch()
    elif run_type == "k_fold":
        # k_fold_test
        k_fold_test()
    else:
        logger.error("不支持的类型...")


if __name__ == '__main__':
    init()
    run()
