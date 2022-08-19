## xgboost 训练
import os, sys

cwd = os.getcwd()
src = "/".join(cwd.split(os.sep)[:-3])
base_path = "/".join(cwd.split(os.sep)[:-4])
sys.path.append(f"{src}{os.sep}")
sys.path.append(f"{base_path}{os.sep}")

from preprocess.field_select import FieldSelect


def process_demo():
    dic_config = {
        "logger": 1,
        "dev": True,
        "origin_path": "../../../../data/xgboost_lr/etl/criteo_sampled_data_no_header.csv",
        "split_cols_file_path": "../../../../data/xgboost_lr/preprocess/criteo_sampled_data_no_header_select_col.csv",
        "encode_file_path": "../../../../data/xgboost_lr/feature/criteo_sampled_data_no_header_encode.csv",

        "train_file_path": "../../../../data/xgboost_lr/feature/criteo_sampled_data_no_header_encode_train.csv",
        "vali_file_path": "../../../../data/xgboost_lr/feature/criteo_sampled_data_no_header_encode_vali.csv",
        "test_file_path": "../../../../data/xgboost_lr/feature/criteo_sampled_data_no_header_encode_test.csv",

        "out_label_path": "../../../../data/xgboost_lr/feature/label.out",
        "out_label_detail_path": "../../../../data/xgboost_lr/feature/label_detail.json",
        "out_one_hot_encoder_path": "../../../../data/xgboost_lr/feature/one_hot_encode.out",
        "file_separator": ",",
        "need_label_encode_cols_num": 26,
        "select_cols": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
                        21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39],
        "split_file_type": "train",
        # "dense_feature_type": "none",
        "dense_feature_type": "minmaxscaler",
        "mms_save_file": "../../../../data/xgboost_lr/feature/mms.save",


    }
    fp = FieldSelect(dic_config)

    fp.label_encode_data()
    if dic_config['dev']:
        print("开始拆分文件")
        fp.split_data()


if __name__ == '__main__':
    process_demo()
