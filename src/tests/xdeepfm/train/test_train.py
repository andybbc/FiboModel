import os, sys

cwd = os.getcwd()
src = "/".join(cwd.split(os.sep)[:-3])
base_path = "/".join(cwd.split(os.sep)[:-4])
sys.path.append(f"{src}{os.sep}")
sys.path.append(f"{base_path}{os.sep}")

from train.xdeepfm import XDeepFMTrain
from conf.rtb.model import CONFIG as model_config
from conf.rtb.preprocess import CONFIG as preprocess_config


def process_demo():
    dic_config = {
        "logger": 1,
        "encode_file_path": "../../../../data/xdeepfm/feature/criteo_sampled_data_no_header_encode.csv",
        "out_label_path": "../../../../data/xdeepfm/feature/label.out",
        "out_label_detail_path": "../../../../data/xdeepfm//label_detail.json",
        "out_one_hot_encoder_path": "../../../../data/xdeepfm//one_hot_encode.out",
        "file_separator": "#",
        "need_label_encode_cols_num": 17,
        "select_cols": [0, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 24, 25, 29, 30, 36, 37, 45, 46, 50, 51, 57, 58, 61],
        "split_file_type": "train",
        "if_minmaxscaler": True,
        "mms_save_file": "../../../../data/xdeepfm/mms.save",
        "xdeepfm_model_path": '../../../../data/xdeepfm/train/xdeepfm_model.h5',
        'model_config': model_config,
        "preprocess_config": preprocess_config
    }

    dft = XDeepFMTrain(dic_config)
    dft.load_data_and_get_feature_names()
    dft.train()


if __name__ == '__main__':
    process_demo()
