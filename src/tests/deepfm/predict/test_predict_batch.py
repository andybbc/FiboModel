import os,sys

cwd = os.getcwd()
src = "/".join(cwd.split(os.sep)[:-3])
base_path = "/".join(cwd.split(os.sep)[:-4])
sys.path.append(f"{src}{os.sep}")
sys.path.append(f"{base_path}{os.sep}")

from predict.deepfm import DeepFmPredict
from conf.rtb.model import CONFIG as model_config
from conf.rtb.preprocess import CONFIG as preprocess_config

def process_demo():
    dic_config = {
        'preprocess_config': preprocess_config,
        "model_config": model_config,
        "file_separator": ",",
        "logger": 1,
        "split_cols_file_path": "../../../../data/preprocess/deepfm/preprocess/criteo_sampled_data_no_header_need_predict_split.csv",
        "encode_file_path": "../../../../data/deepfm/feature/criteo_sampled_data_no_header_need_predict_split_encode.csv",
        "out_label_path": "../../../../data/deepfm/feature/label.out",
        "out_label_detail_path": "../../../../data/deepfm/feature/label_detail.json",
        "predict_input_file_path": '../../../../data/deepfm/feature/criteo_sampled_data_no_header_need_predict_encode.csv',
        "need_label_encode_cols_num": 26,
        "select_cols": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
                        21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39],
        "deepfm_model_path": '../../../../data/deepfm/train/deepfm_model.h5',
        "predict_output_file_path": "../../../../data/deepfm/predict/criteo_sampled_data_no_header_pred_res.txt"
    }

    dfp = DeepFmPredict(dic_config)
    dfp.predict_batch()

def process_product():
    dic_config = {
        'preprocess_config': preprocess_config,
        "model_config": model_config,
        "file_separator": "#",
        "logger": 1,
        "split_cols_file_path": "../../../../data/preprocess/deepfm_product/preprocess/test.txt",
        "out_label_path": "../../../../data/deepfm_product/feature/label.out",
        "out_label_detail_path": "../../../../data/deepfm_product/feature/label_detail.json",
        "predict_input_file_path": "../../../../data/deepfm_product/feature/test_encode.txt",
        "need_label_encode_cols_num": 11,
        "select_cols": [0, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
        "deepfm_model_path": '../../../../data/deepfm_product/train/deepfm_model.h5',
        "predict_output_file_path": "../../../../data/deepfm_product/predict/test_res.txt"
    }

    dfp = DeepFmPredict(dic_config)
    dfp.predict_batch()

# 生产测试
if __name__ == '__main__':
    # process_demo()
    process_product()

