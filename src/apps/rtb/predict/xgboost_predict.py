'''
rtb预估点击率,输入数据格式: label列,数值型特征列,需要label_encode的列
已经是label_encode好的文件
'''


import sys
sys.path.append("..")
sys.path.append("../..")
sys.path.append("../../../..")

from predict.xgboost_lr_rtb import XgbLRPredict
import gflags
from utils import logs
from conf.rtb.model import CONFIG as model_config
from conf.rtb.preprocess import CONFIG as preprocess_config

Flags = gflags.FLAGS
gflags.DEFINE_string('log_path', '../../../../logs/xgboost.log', 'log')

# 各种文件路径
# gflags.DEFINE_string('in_one_hot_encoder_path', "../../../../data/xgb_lr_demo_new/new_no_request_id/one_hot.out",'onehot fit之后的内存文件,保存下来为预估用')  # 通过序列化来做

gflags.DEFINE_string('in_predict_input_file', "../../../../data/xgb_lr_demo_new/new_no_request_id/new_need_predict_sample_encode.csv", '预估输入文件')
gflags.DEFINE_string('out_predict_output_file', "../../../../data/xgb_lr_demo_new/new_no_request_id/new_predict_res_sample.csv", '预估输出文件')

# 保存的model文件
gflags.DEFINE_string('in_xgb_model_path', "../../../../data/xgb_lr_demo_new/new_no_request_id/xgb_model.pkl", 'xgb_model_path')

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
    dic_config['use_model_type'] = 'xgboost'  # 使用的模型的种类

    logger.info(f"=========================开始: 预估 =========================")

    dic_config["predict_input_file_path"] = Flags.in_predict_input_file  # 需要被预估的原始文件的路径,列只包括click往后的字段
    dic_config['predict_output_file_path'] = Flags.out_predict_output_file

    # dic_config["out_one_hot_encoder_path"] = Flags.in_one_hot_encoder_path  # map,转换列的数据,label_encode

    dic_config["file_separator"] = preprocess_config['common']['file_separator']  # 每一行文件分隔符
    dic_config['select_cols'] = preprocess_config['common']['select_cols']

    dic_config["xgb_model_path"] = Flags.in_xgb_model_path
    # dic_config["lr_model_path"] = Flags.in_lr_model_path

    dic_config['need_label_encode_cols_num'] = preprocess_config['common']['need_label_encode_cols_num']

# 输入的格式要和训练的格式一样
def predict():
    # 预测数据,需要model文件和测试文件
    logger.info("""
            ##########################################
            ##### XGBoost Predict_Batch START #####
            ##########################################
            """)
    xgb_lr_predict = XgbLRPredict(dic_config)
    xgb_lr_predict.predict_batch_xgb()

    logger.info("""
                ##########################################
                ##### XGBoost Predict_Batch DONE #####
                ##########################################
                """)

def run():
    # 预测数据,需要model文件和测试文件
    predict()

if __name__ == '__main__':
    init()
    run()