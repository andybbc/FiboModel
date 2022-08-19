# -*- coding:utf-8 -*-

import sys
sys.path.append("..")

import numpy as np
from sklearn.datasets import load_iris
from sklearn.utils import shuffle
from model.k_nearest_neighbor import KNearestNeighbor as KNNModel
from model.k_nearest_neighbor import KNearestNeighbor as KNNPredict


dic_config = {
    'num_folds': 5,
    'k_choices': [1, 3, 5, 8, 10, 12, 15, 20, 50, 100]
}


# 生成训练、校验使用数据
def data_generate():
    iris = load_iris()
    X, y = shuffle(iris.data, iris.target, random_state=13)
    X = X.astype(np.float32)
    
    # 训练集和测试集比例（7：3）
    offset = int(X.shape[0] * 0.7)
    X_train, y_train = X[:offset], y[:offset]
    X_test, y_test = X[offset:], y[offset:]
    
    y_train = y_train.reshape((-1,1))
    y_test = y_test.reshape((-1,1))
    
    return X_train, y_train, X_test, y_test


def train():
    # 加载数据集
    X_train, y_train, X_test, y_test = data_generate()

    # 加载模型
    model = KNNModel(dic_config)

    # 训练
    model.fit(X_train, y_train)


def predict():
    # 加载模型
    model = KNNPredict(dic_config)
    # model.load_model(model_path)


if __name__ == '__main__':
    train()
    predict()
