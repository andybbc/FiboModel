# -*- coding:utf-8 -*-

import sys
sys.path.append("..")

import numpy as np
from matplotlib import pyplot as plt
from model.linear_regression import LinearRegression as LRModel
from predict.linear_regression import LinearRegression as LRPredict


dic_config = {
    'alpha': 0.02,
    'n_iter': 1000,
    'store_path': '../data/LinearR_storage.txt'
}


# 生成训练、校验使用数据
def data_generate():
    # 随机生成100个数据
    X_train = np.random.randn(100)
    
    # 误差系数
    theta = 0.5
    
    # 为数据添加干扰
    y_train = 5.20 * X_train + 7.29 + theta * np.random.randn(100)
    
    # 随机生成10个校验数据集
    X_test = np.random.randn(10)
    y_test = 5.20 * X_test + 7.29 + theta * np.random.randn(10)
    
    return X_train, y_train, X_test, y_test


def train():
    # 加载数据集
    X_train, y_train, X_test, y_test = data_generate()

    # 加载模型
    model = LRModel(dic_config)

    # 训练
    model.fit(X_train, y_train)

    # 预估参数
    print(model._w, model._b)

    # 画出损失值随迭代次数的变化图
    plt.plot(model.cost)
    plt.show()

    # 画出样本散点对比图以及模型的预测图
    model.plotFigure(X_test, y_test)
    
    # 存储
    model.store_model(dic_config.get('store_path'))


def predict():
    # 加载模型
    model = LRPredict(dic_config)
    w = model.load_model(dic_config.get('store_path'))
    
    # 加载数据集
    X_train, y_train, X_test, y_test = data_generate()
    
    y_pred = model.predict(X_test, w[0], w[1])
    print(y_pred)


if __name__ == '__main__':
    # train()
    predict()
