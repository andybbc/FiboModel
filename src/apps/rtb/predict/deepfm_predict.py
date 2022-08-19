'''
rtb预估点击率,输入数据格式: label列,数值型特征列,需要label_encode的列
已经是label_encode好的文件
'''

import gflags
import sys

sys.path.append("..")
sys.path.append("../..")
sys.path.append("../../../..")

from predict.deepfm import DeepFmPredict
from utils import logs
from conf.rtb.model import CONFIG as model_config
from conf.rtb.preprocess import CONFIG as preprocess_config

Flags = gflags.FLAGS

gflags.DEFINE_string('log_path', '../../../../logs/xgboost_lr.log', 'log')

gflags.DEFINE_string('in_predict_input_file',
                     "../../../../data/deepfm/criteo_sampled_data_no_header_pred_input_encode.csv", '预估输入文件')
gflags.DEFINE_string('out_predict_output_file', "../../../../data/deepfm/criteo_sampled_data_no_header_pred_res.txt",
                     '预估输出文件')

# 保存的model文件
gflags.DEFINE_string('in_deepfm_model_path', "../../../../data/deepfm/deepfm_model.h5", 'deepfm_model_path')
gflags.DEFINE_string('predict_type', "predict_batch", 'predict_batch / predict_one')

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

    logger.info(f"=========================开始: 预估 =========================")

    dic_config["predict_input_file_path"] = Flags.in_predict_input_file  # 需要被预估的原始文件的路径,列只包括click往后的字段
    dic_config['predict_output_file_path'] = Flags.out_predict_output_file

    dic_config["file_separator"] = preprocess_config['common']['file_separator']  # 每一行文件分隔符
    dic_config['select_cols'] = preprocess_config['common']['select_cols']
    dic_config["deepfm_model_path"] = Flags.in_deepfm_model_path  # deepfm模型文件
    dic_config['need_label_encode_cols_num'] = preprocess_config['common']['need_label_encode_cols_num']


# 输入的格式要和训练的格式一样
def predict():
    if Flags.predict_type == "predict_batch":
        # 预测数据,需要model文件和测试文件
        logger.info("""
                ##########################################
                ##### DEEPFM Predict_Batch START #####
                ##########################################
                """)

        deepfm_predict = DeepFmPredict(dic_config)
        deepfm_predict.predict_batch()

    elif Flags.predict_type == "predict_one":
        # 预测数据,需要model文件和测试文件
        logger.info("""
                       ##########################################
                       ##### DEEPFM PredictOne START #####
                       ##########################################
                       """)
        deepfm_predict = DeepFmPredict(dic_config)
        print("输入exit结束")
        while True:
            try:
                inputStr = input("请输入待预测的list")
                deepfm_predict.predict_one(inputStr)
            except Exception as e:
                print("输入错误: %s", e)

    else:
        raise Exception("未知的预测类型")


def run():
    # 预测数据,需要model文件和测试文件
    predict()


if __name__ == '__main__':
    init()
    run()
