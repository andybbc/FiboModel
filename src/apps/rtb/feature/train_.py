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

# train/predict 如果是train,原始文件label_encode为文件生成,如果是predict,label_encode为保存的model去置换
gflags.DEFINE_string('in_file', '../../../../data/deepfm/criteo_sampled_data_no_header_select_col.csv', '由原始文件选定的列')
gflags.DEFINE_string('out_encode_file', '../../../../data/deepfm/criteo_sampled_data_no_header_encode.csv', '转换后的label_encode文件')

gflags.DEFINE_string('out_label_path', "../../../../data/deepfm/label.out", '字段映射')  # 通过序列化来做
# label的映射关系,打算用json装起来,导出来
gflags.DEFINE_string('out_label_detail_path', "../../../../data/deepfm/label_detail.json", 'test_file_path')

# 拆分文件,xgboost可能用到
gflags.DEFINE_string('out_train_file', "../../../../data/xgb_lr_demo_new/new_no_request_id/new_sample_train.csv", 'train_file_path')
gflags.DEFINE_string('out_vali_file', "../../../../data/xgb_lr_demo_new/new_no_request_id/new_sample_vali.csv", 'vali_file_path')
gflags.DEFINE_string('out_test_file', "../../../../data/xgb_lr_demo_new/new_no_request_id/new_sample_test.csv", 'test_file_path')

# 数值字段MinMaxScale处理
gflags.DEFINE_string('out_mms_save_file', "../../../../data/deepfm/mms.save", 'MinMaxScale中间文件')
gflags.DEFINE_string('out_tne_file', "../../../../data/deepfm/tne.jpg", 'tne散点图')



dic_config = {}

gflags.FLAGS(sys.argv)
logger = logs.Logger(log_path=Flags.log_path).logger


def init():
    global dic_config
    global logger
    dic_config['logger'] = logger
    dic_config['split_file_type'] = "train"

    dic_config['model_config'] = model_config  # xgb训练的参数
    dic_config['preprocess_config'] = preprocess_config  # xgb训练的参数

    dic_config['dev'] = preprocess_config['common']['dev']  # Boolean类型,是否需要拆分
    dic_config['split_cols_file_path'] = Flags.in_file
    dic_config["out_label_path"] = Flags.out_label_path  # 二进制label转换
    dic_config['out_label_detail_path'] = Flags.out_label_detail_path  # json文件,映射关系
    dic_config["encode_file_path"] = Flags.out_encode_file  # 输入文件
    dic_config["file_separator"] = preprocess_config['common']['file_separator']  # 每一行文件分隔符

    dic_config["train_file_path"] = Flags.out_train_file  # 拆分后训练的数据
    dic_config["vali_file_path"] = Flags.out_vali_file  # 拆分后
    dic_config["test_file_path"] = Flags.out_test_file  # 拆分后

    dic_config['select_cols'] = preprocess_config['common']['select_cols']
    dic_config['need_label_encode_cols_num'] = preprocess_config['common']['need_label_encode_cols_num']
    # dic_config['if_minmaxscaler'] = preprocess_config['common']['if_minmaxscaler']  # 数值部分是否做归一化处理
    dic_config['dense_feature_type'] = preprocess_config['common']['dense_feature_type']  # minmaxscaler / log / none
    dic_config['mms_save_file'] = Flags.out_mms_save_file  # mms的中间文件
    dic_config['tne_file_path'] = Flags.out_tne_file  # tne散点图
    logger.info(f"=========================开始:文件预处理=========================")


def run():
    field_select =FieldSelect(dic_config)
    print("开始预处理训练文件label_encode")
    field_select.label_encode_data()
    if dic_config['dev']:
        print("开始拆分文件")
        field_select.split_data()
        # print("打印tne散点图")
        # field_select.show_tne()


if __name__ == '__main__':
    init()
    run()