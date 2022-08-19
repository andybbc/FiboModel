import sys

from preprocess.segment_words import segment_words
from .base import Base
from model._xgboost import XGBoost as xgb_model
from sklearn.model_selection import train_test_split
from conf.reco._xgboost import train_params
import pandas as pd

sys.path.append('../model')

class _xgboost(Base):

    def __init__(self, dic_config):
        Base.__init__(self, dic_config)
        self.data_path = dic_config['data_path']
        self.dic_config = dic_config

    def load_data(self):
        data = pd.read_csv(self.data_path, header=None, sep=',')
        cols_num = data.shape[1]
        # data.rename(columns={cols_num: 'label'}, inplace=True)
        X = data.iloc[:, :cols_num - 1]
        Y = data.iloc[:, cols_num - 1]

        self.logger.info(f"训练数据:训练集 X shape:{X.shape}, Y shape:{Y.shape}")

        self.logger.info(f"数据集拆分 test_size:{train_params['test_size']} ,random_state:{train_params['random_state']}")
        X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=train_params['test_size'],
                                                            random_state=train_params['random_state'])
        return X_train, X_test, y_train, y_test

    def train(self, x_train, x_test, y_train, y_test):
        xgboost_model = xgb_model(self.dic_config)
        bst = xgboost_model.train(x_train, x_test, y_train, y_test)  # Booster
        # 模型保存
        bst.save_model(self.dic_config['model_path'])

    def k_fold_test(self):
        data = pd.read_csv(self.data_path, header=None, sep=',')
        xgboost_model = xgb_model(self.dic_config)
        cols_num = data.shape[1]
        train_x = data.iloc[:, :cols_num - 1]
        train_y = data.iloc[:, cols_num - 1]

        xgboost_model.k_fold_test(data,train_x, train_y)

        pass


    def text_train(self):
        sw = segment_words(self.dic_config)
        train_content, train_option = sw.text_load_train_data()
        xgboost_model = xgb_model(self.dic_config)
        bst = xgboost_model.text_train(train_content, train_option)
        # 模型保存
        bst.save_model(self.dic_config['model_path'])

