'''
rtb预估点击率,输入数据格式: label列,数值型特征列,需要label_encode的列
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

gflags.DEFINE_string('in_split_cols_file', '../../../../data/xgboost/preprocess/criteo_sampled_data_no_header_need_predict_select_col.csv', '由原始文件选定的列')
gflags.DEFINE_string('out_encode_file', '../../../../data/xgboost/feature/criteo_sampled_data_no_header_need_predict_encode.csv', '转换后的label_encode文件')

gflags.DEFINE_string('in_label_path', "../../../../data/xgboost/feature/label.out", '字段映射')  # 通过序列化来做
# 拆分文件
gflags.DEFINE_string('train_file', "../../../../data/xgb_lr_demo_new/new_no_request_id/new_sample_train.csv", 'train_file_path')
gflags.DEFINE_string('vali_file', "../../../../data/xgb_lr_demo_new/new_no_request_id/new_sample_vali.csv", 'vali_file_path')
gflags.DEFINE_string('test_file', "../../../../data/xgb_lr_demo_new/new_no_request_id/new_sample_test.csv", 'test_file_path')


# 数值字段MinMaxScale处理
gflags.DEFINE_string('in_mms_save_file', "../../../../data/xgb_lr_demo_new/new_no_request_id/mms.save", 'MinMaxScale中间文件')


dic_config = {}

gflags.FLAGS(sys.argv)
logger = logs.Logger(log_path=Flags.log_path).logger


def init():
    global dic_config
    global logger
    dic_config['logger'] = logger
    dic_config['split_file_type'] = "predict"

    dic_config['model_config'] = model_config  # xgb训练的参数
    dic_config['preprocess_config'] = preprocess_config  # xgb训练的参数

    dic_config['dev'] = preprocess_config['common']['dev']  # Boolean类型,是否需要拆分
    dic_config["out_label_path"] = Flags.in_label_path  # 输入文件
    dic_config['split_cols_file_path'] = Flags.in_split_cols_file
    dic_config["encode_file_path"] = Flags.out_encode_file  # 输入文件
    dic_config["file_separator"] = preprocess_config['common']['file_separator']  # 每一行文件分隔符

    dic_config['select_cols'] = preprocess_config['common']['select_cols']
    dic_config['need_label_encode_cols_num'] = preprocess_config['common']['need_label_encode_cols_num']
    # dic_config['if_minmaxscaler'] = preprocess_config['common']['if_minmaxscaler']  # 数值部分是否做归一化处理
    dic_config['dense_feature_type'] = preprocess_config['common']['dense_feature_type']  # minmaxscaler / log / none
    dic_config['mms_save_file'] = Flags.in_mms_save_file  # mms的中间文件
    logger.info(f"=========================开始:文件预处理=========================")


def run():
    field_select = FieldSelect(dic_config)
    print("开始预处理预测文件label_encode")
    field_select.label_encode_data()
    logger.info(f"=========================文件 feature 完成=========================")

if __name__ == '__main__':
    init()
    run()