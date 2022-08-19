import sys
import joblib
import pickle

sys.path.append("..")
sys.path.append("../..")
from .base import Base
import pandas as pd
import numpy as np
from model.xgboost_rtb import XgboostRTBModel
from model.logistic_regression_rtb import LogisticRegressionRTBModel


class XgbLRPredict(Base):

    def __init__(self, dic_config):
        super().__init__(dic_config)
        self.dic_config = dic_config

        self.use_model_type = dic_config['use_model_type']  # 使用的模型类型 xgbgoot, xgboost_lr
        self.xgb_model = joblib.load(dic_config['xgb_model_path'])  # 肯定要加载的
        self.out_one_hot_encoder_path = dic_config.get('out_one_hot_encoder_path')

        # 如果是用LR,先要加载one-hot-encode的文件
        if self.use_model_type == 'xgboost_lr':
            self.lr_model = joblib.load(dic_config['lr_model_path'])
            # 加载one_hot_encode的文件
            with open(self.out_one_hot_encoder_path, 'rb') as f:
                self.one_hot_encoder = pickle.load(f)

        self.xgboost_model_entity = XgboostRTBModel(dic_config)
        self.lr_model_entity = LogisticRegressionRTBModel(dic_config)

    def predict_batch_xgb(self):
        # 需要被预估的原始数据,id列和click没有,只有后面的
        need_pred_df = pd.read_csv(self.dic_config['predict_input_file_path'], header=None,
                                   sep=self.dic_config['file_separator'], encoding=u'utf-8')
        cols_num = need_pred_df.shape[1]
        need_pred_df.columns = [index for index in range(1, cols_num + 1)]  # 将列名转换成1,2,3,4,,,,不要从0开始

        probas = self.xgboost_model_entity.predict_proba(self.xgb_model, need_pred_df)
        predict_out_path = self.dic_config['predict_output_file_path']
        np.savetxt(predict_out_path, probas[:, 1])  # 只输出为1的概率

    def predict_batch_xgb_lr(self):
        need_pred_df = pd.read_csv(self.dic_config['predict_input_file_path'], header=None,
                                   sep=self.dic_config['file_separator'], encoding=u'utf-8')
        cols_num = need_pred_df.shape[1]
        need_pred_df.columns = [index for index in range(1, cols_num + 1)]  # 将列名转换成1,2,3,4,,,,不要从0开始

        ##apply函数返回的是叶子索引
        x_test_leaves = self.xgb_model.apply(need_pred_df).astype(np.int32)
        # one-hot-encode转下
        x_test_lr = self.one_hot_encoder.transform(x_test_leaves).toarray()
        probas = self.lr_model_entity.predict_proba(self.lr_model, x_test_lr)
        np.savetxt(self.dic_config['predict_output_file_path'], probas[:, -1])  # 只取最后一个,预测为1的概率

    def predict_one_xgb(self, need_pred_df):
        cols_num = need_pred_df.shape[1]
        need_pred_df.columns = [index for index in range(1, cols_num + 1)]
        probas = self.xgboost_model_entity.predict_proba(self.xgb_model, need_pred_df)
        return probas[0, 1]

    def predict_one_xgb_lr(self, need_pred_df):
        cols_num = need_pred_df.shape[1]
        need_pred_df.columns = [index for index in range(1, cols_num + 1)]
        ##apply函数返回的是叶子索引
        x_test_leaves = self.xgb_model.apply(need_pred_df).astype(np.int32)
        # one-hot-encode转下
        x_test_lr = self.one_hot_encoder.transform(x_test_leaves).toarray()
        # probas = self.lr_model_entity.predict_proba(self.lr_model, x_test_lr[: -1])
        probas = self.lr_model_entity.predict_proba(self.lr_model, x_test_lr)
        return probas[0, 1]
