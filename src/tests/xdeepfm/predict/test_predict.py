import os,sys

cwd = os.getcwd()
src = "/".join(cwd.split(os.sep)[:-3])
base_path = "/".join(cwd.split(os.sep)[:-4])
sys.path.append(f"{src}{os.sep}")
sys.path.append(f"{base_path}{os.sep}")

from predict.xdeepfm import XDeepFmPredict
from conf.rtb.model import CONFIG as model_config
from conf.rtb.preprocess import CONFIG as preprocess_config

def process_demo():
    dic_config = {
        'preprocess_config': preprocess_config,
        "model_config": model_config,
        "file_separator": "#",
        "logger": 1,
        "split_cols_file_path": "../../../../data/preprocess/xdeepfm/preprocess/criteo_sampled_data_no_header_need_predict_split.csv",
        "encode_file_path": "../../../../data/xdeepfm/feature/criteo_sampled_data_no_header_need_predict_split_encode.csv",
        "out_label_path": "../../../../data/xdeepfm/feature/label.out",
        "out_label_detail_path": "../../../../data/xdeepfm/feature/label_detail.json",
        "predict_input_file_path": '../../../../data/xdeepfm/feature/criteo_sampled_data_no_header_need_predict_encode.csv',
        "need_label_encode_cols_num": 17,
        "select_cols": [0, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 24, 25, 29, 30, 36, 37, 45, 46, 50, 51, 57, 58, 61],
        "xdeepfm_model_path": '../../../../data/xdeepfm/train/xdeepfm_model.h5',
        "predict_output_file_path": "../../../../data/xdeepfm/predict/criteo_sampled_data_no_header_pred_res.txt"
    }

    dfp = XDeepFmPredict(dic_config)
    dfp.predict_batch()


if __name__ == '__main__':
    process_demo()
