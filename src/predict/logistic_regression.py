#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from .base import Base

import numpy as np

def sigmoid(x):
    return 1 / (1 + np.exp(-x))

class LogisticRegression():

    def __init__(self, dic_config={}):
        Base.__init__(self, dic_config)
        pass

    # 加载模型参数
    def loadModel(self, filename):
        import pickle
        try:
            with open(filename, 'rb') as file:
                self.model = pickle.load(file)
        except:
            print("=== Load model._w ERROR")

    def predict(self, X):
        if (len(X.shape) == 1):
            # 兼容单一实例
            X = [X]

        X = np.insert(X, 0, 1, axis = 1)
        y_pred = np.round(sigmoid(X.dot(self.model)))
        y_pred = np.reshape(y_pred, X.shape[0])
        
        return y_pred[0].astype(int)