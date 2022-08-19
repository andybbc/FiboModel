import sys

from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import OneHotEncoder

sys.path.append("..")
import numpy as np
from model.base import Base
import xgboost as xgb


class LogisticRegressionRTBModel(Base):

    def __init__(self, dic_config):
        super().__init__(dic_config)
        self.dic_config = dic_config
        self.lr_model = LogisticRegression(max_iter=10000)

    def train(self, x_train, y_train):

        self.lr_model.fit(x_train, y_train)
        return self.lr_model

    def predict_proba(self, trainedmodel, x_test):
        probas = trainedmodel.predict_proba(x_test)
        return probas

    def predict(self, trainedmodel, x_test):
        res = trainedmodel.predict(x_test)
        return res

    '''
    def train(self, xgb_model, x_train, y_train, x_test):
        """
        model: train_xgb 方法的返回
        """
        ##apply函数返回的是叶子索引
        x_train_leaves = xgb_model.apply(x_train).astype(np.int32)
        x_test_leaves = xgb_model.apply(x_test).astype(np.int32)
        # print(" = " * 10)
        # print(type(x_train_leaves))  # <class 'numpy.ndarray'>
        # print(x_train_leaves.shape)  # (559999, 10)
        # print(x_train_leaves)
        # print(" = " * 10)

        # 使用numpy的concatenate来拼接数组，并生成全局的onehot，单一使用train的可能会漏掉编码，test验证的时候出问题
        x_leaves = np.concatenate((x_train_leaves, x_test_leaves), axis=0)  # axis=0二维纵向拼接,union

        # print(f'Transform xgb leaves shape: {x_leaves.shape}')  # (859999, 10)

        xgb_onehotcoder = OneHotEncoder()
        xgb_onehotcoder.fit(x_leaves)

        self.x_train_lr = xgb_onehotcoder.transform(x_train_leaves).toarray()  # 转成one-hot编码
        x_test_lr = xgb_onehotcoder.transform(x_test_leaves).toarray()  # 转成one-hot编码

        # print(f'Transform xgb x_train_lr shape: {x_train_lr.shape}')  # (559999, 0)
        # print(f'Transform xgb x_test_lr shape: {x_test_lr.shape}')  # (300000, 80)

        lr_model = LogisticRegression()
        lr_model.fit(self.x_train_lr, y_train)

        return lr_model
    '''
