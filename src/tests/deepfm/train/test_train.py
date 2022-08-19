import os,sys

cwd = os.getcwd()
src = "/".join(cwd.split(os.sep)[:-3])
base_path = "/".join(cwd.split(os.sep)[:-4])
sys.path.append(f"{src}{os.sep}")
sys.path.append(f"{base_path}{os.sep}")


from conf.rtb.model import CONFIG as model_config
from conf.rtb.preprocess import CONFIG as preprocess_config

from train.deepfm import DeepFMTrain


def process_demo():
    dic_config = {
        "logger": 1,
        "encode_file_path": "../../../../data/deepfm/feature/criteo_sampled_data_no_header_encode.csv",
        "out_label_path": "../../../../data/deepfm/feature/label.out",
        "out_label_detail_path": "../../../../data/deepfm//label_detail.json",
        "out_one_hot_encoder_path": "../../../../data/deepfm//one_hot_encode.out",
        "file_separator": ",",
        "need_label_encode_cols_num": 26,
        "select_cols": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
                        21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39],
        "split_file_type": "train",
        "if_minmaxscaler": True,
        "mms_save_file": "../../../../data/deepfm/mms.save",
        "deepfm_model_path": '../../../../data/deepfm/train/deepfm_model.h5',
        'model_config': model_config,
        "preprocess_config": preprocess_config
    }

    dft = DeepFMTrain(dic_config)
    dft.load_data_and_get_feature_names()
    dft.train()


def process_product():
    dic_config = {
        "logger": 1,
        "encode_file_path": "../../../../data/deepfm_product/feature/train_encode.txt",
        "out_label_path": "../../../../data/deepfm_product/feature/label.out",
        "out_label_detail_path": "../../../../data/deepfm_product/feature/label_detail.json",
        "out_one_hot_encoder_path": "../../../../data/deepfm_product/train/one_hot_encode.out",
        "file_separator": "#",
        "need_label_encode_cols_num": 11,
        "select_cols": [0, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
        "split_file_type": "train",
        "dense_feature_type": "minmaxscaler",
        "mms_save_file": "../../../../data/deepfm_product/mms.save",
        "deepfm_model_path": '../../../../data/deepfm_product/train/deepfm_model.h5',
        'model_config': model_config,
        "preprocess_config": preprocess_config,
    }

    dft = DeepFMTrain(dic_config)
    dft.load_data_and_get_feature_names()
    dft.train()


if __name__ == '__main__':
    # process_demo()
    process_product()
