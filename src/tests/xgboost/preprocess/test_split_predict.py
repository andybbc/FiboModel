## deepfm 训练
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
        "origin_path": "../../../../data/xgboost/etl/criteo_sampled_data_no_header_need_predict.csv",
        "split_cols_file_path": "../../../../data/xgboost/preprocess/criteo_sampled_data_no_header_need_predict_select_col.csv",
        "encode_file_path": "../../../../data/xgboost/feature/criteo_sampled_data_no_header_need_predict_encode.csv",
        "out_label_path": "../../../../data/xgboost/feature/label.out",
        "out_label_detail_path": "../../../../data/xgboost/feature/label_detail.json",
        "out_one_hot_encoder_path": "../../../../data/xgboost/feature/one_hot_encode.out",
        "file_separator": "#",
        "need_label_encode_cols_num": 20,
        "select_cols": [0, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
                        31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60],
        "split_file_type": "predict",
        # "dense_feature_type": "log",
        "dense_feature_type": "none",
        "mms_save_file": "../../../../data/xgboost/feature/mms.save",
    }
    fp = FieldSelect(dic_config)

    fp.split_file_cols()


if __name__ == '__main__':
    process_demo()
