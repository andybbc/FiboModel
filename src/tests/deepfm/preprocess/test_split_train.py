## deepfm 训练
import os,sys

cwd = os.getcwd()
src = "/".join(cwd.split(os.sep)[:-3])
base_path = "/".join(cwd.split(os.sep)[:-4])
sys.path.append(f"{src}{os.sep}")
sys.path.append(f"{base_path}{os.sep}")

from preprocess.field_select import FieldSelect

def process_demo():
    dic_config = {
        "logger": 1,
        "origin_path": "../../../../data/deepfm/etl/criteo_sampled_data_no_header.csv",
        "split_cols_file_path": "../../../../data/deepfm/preprocess/criteo_sampled_data_no_header_select_col.csv",
        "encode_file_path": "../../../../data/deepfm/feature/criteo_sampled_data_no_header_encode.csv",
        "out_label_path": "../../../../data/deepfm/feature/label.out",
        "out_label_detail_path": "../../../../data/deepfm/feature/label_detail.json",
        "out_one_hot_encoder_path": "../../../../data/deepfm/feature/one_hot_encode.out",
        "file_separator": ",",
        "need_label_encode_cols_num": 26,
        "select_cols": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
                        21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39],
        "split_file_type": "train",
        "dense_feature_type": "log",
        "mms_save_file": "../../../../data/deepfm/feature/mms.save",
    }
    fp = FieldSelect(dic_config)

    fp.split_file_cols()


def process_product():
    dic_config = {
        "logger": 1,
        "origin_path": "../../../../data/deepfm_product/etl/train.txt",
        "split_cols_file_path": "../../../../data/deepfm_product/preprocess/train.txt",
        "encode_file_path": "../../../../data/deepfm_product/feature/train_encode.txt",
        "out_label_path": "../../../../data/deepfm_product/feature/label.out",
        "out_label_detail_path": "../../../../data/deepfm_product/feature/label_detail.json",
        "out_one_hot_encoder_path": "../../../../data/deepfm_product/feature/one_hot_encode.out",
        "file_separator": "#",
        "need_label_encode_cols_num": 11,
        "select_cols": [0, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
        "split_file_type": "train",
        "dense_feature_type": "minmaxscaler",
        "mms_save_file": "../../../../data/deepfm_product/feature/mms.save",
    }
    fp = FieldSelect(dic_config)

    fp.split_file_cols()


# 生产数据测试用
if __name__ == '__main__':
    # process_demo()
    process_product()

