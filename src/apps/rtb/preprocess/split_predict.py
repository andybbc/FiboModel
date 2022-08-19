'''
原始文件按选定的列拆分
'''

import gflags
import sys

sys.path.append("..")
sys.path.append("../..")
sys.path.append("../../../..")

from preprocess.field_select import FieldSelect
from utils import logs

from conf.rtb.model import CONFIG as model_config
from conf.rtb.preprocess import CONFIG as preprocess_config

Flags = gflags.FLAGS
gflags.DEFINE_string('log_path', '../../../../logs/xgboost_lr.log', 'log')

# # train/predict 如果是train,原始文件label_encode为文件生成,如果是predict,label_encode为保存的model去置换
# gflags.DEFINE_string('in_file', '../../../../data/xgb_lr_demo_new/new_no_request_id/new_need_predict_sample.csv', '原始文件')
# gflags.DEFINE_string('out_file', '../../../../data/xgb_lr_demo_new/new_no_request_id/new_need_predict_sample_select_col.csv', '由原始文件选定的列')

gflags.DEFINE_string('in_file', '../../../../data/deepfm/criteo_sampled_data_no_header_pred_input.csv', '原始文件')
gflags.DEFINE_string('out_file', '../../../../data/deepfm/criteo_sampled_data_no_header_pred_input_select_col.csv', '由原始文件选定的列')


dic_config = {}

gflags.FLAGS(sys.argv)
logger = logs.Logger(log_path=Flags.log_path).logger


def init():
    global dic_config
    global logger
    dic_config['logger'] = logger

    dic_config['model_config'] = model_config  # xgb训练的参数
    dic_config['preprocess_config'] = preprocess_config  # xgb训练的参数

    dic_config["origin_path"] = Flags.in_file  # 输入文件
    dic_config["file_separator"] = preprocess_config['common']['file_separator']  # 每一行文件分隔符
    dic_config['select_cols'] = preprocess_config['common']['select_cols']
    dic_config['split_cols_file_path'] = Flags.out_file
    dic_config['split_file_type'] = "predict"

    logger.info(f"=========================开始:文件拆分处理开始=========================")


def run():
    field_select = FieldSelect(dic_config)
    logger.info("开始按照指定的列拆分原始文件")
    field_select.split_file_cols()
    logger.info(f"=========================开始:文件拆分字段完成=========================")

if __name__ == '__main__':
    init()
    run()

