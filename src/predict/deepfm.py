import sys

sys.path.append("..")
sys.path.append("../..")
sys.path.append("../../..")

from model.deepfm_rtb import DeepFMModel
from model.base import Base
import pandas as pd
from keras.models import load_model
from deepctr.layers import custom_objects
import numpy as np

class DeepFmPredict(Base):

    def __init__(self, dic_config):
        super().__init__(dic_config)
        self.dic_config = dic_config

        self.deepfm_model_path = dic_config['deepfm_model_path']
        self.deepfm_model = DeepFMModel(dic_config)

    def predict_batch(self):
        # 这边是已经预处理过的文件
        need_pred_df = pd.read_csv(self.dic_config['predict_input_file_path'], header=None,
                                   sep=self.dic_config['file_separator'], encoding=u'utf-8')
        need_pred_df.columns = list(str(i) for i in range(1, len(self.dic_config['select_cols'])))
        # print(need_pred_df.columns)
        test_model_input = {name: need_pred_df[name] for name in need_pred_df.columns}

        deepfm_model = load_model(self.deepfm_model_path, custom_objects)
        # print(type(deepfm_model))

        pred_ans = self.deepfm_model.predict(deepfm_model, test_model_input)
        np.savetxt(self.dic_config['predict_output_file_path'], pred_ans)

    def predict_one(self, need_pred_df):

        test_model_input = {name: need_pred_df[name] for name in need_pred_df.columns}
        if not hasattr(self, 'deepfm_model_predict'):
            self.deepfm_model_predict = load_model(self.deepfm_model_path, custom_objects)  # 不要每次都加载

        pred_ans = self.deepfm_model.predict(self.deepfm_model_predict, test_model_input)
        return pred_ans


