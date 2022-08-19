# -*- coding:utf-8 -*-

import numpy as np
from matplotlib import pyplot as plt


class LinearRegression():
    '''
    线性回归类
    参数：
        alpha: 迭代步长
        n_iter:迭代次数
    使用示例：
        lr = LinearRegression()          # 实例化类
        lr.initialPara(w_start, b_start) # 初始化预估参数
        lr.fit(X_train,y_train)          # 训练模型
        y_predict = lr.predict(X_test)   # 预测训练数据
        lr.plotFigure()                  # 用于画出样本散点图与预测模型
    '''
    def __init__(self, dic_config={}):
        self._alpha = dic_config.get('alpha', 0.02)      # 步长
        self._n_iter = dic_config.get('n_iter', 1000)    # 最大迭代次数

    # 初始化模型参数
    def initialPara(self, w_start=0, b_start=0):
        self._w = w_start
        self._b = b_start

    # 训练模型
    def fit(self, X_train, y_train):
        # 保存原始数据
        self.X_source = X_train.copy()
        self.y_source = y_train.copy()

        # 获取训练样本个数
        sample_num = X_train.shape[0]

        # 初始化w，b
        self.initialPara()

        # 创建列表存放每次每次迭代后的损失值
        self.cost = []

        # 开始训练迭代
        for _ in range(self._n_iter):
            # 计算预估值和偏差
            y_predict = self.predict(X_train)
            y_bias = y_train - y_predict
            
            # 记录损失评价值（均方差）
            self.cost.append(np.dot(y_bias,y_bias)/(2 * sample_num))
            
            # 梯度下降处理预估参数
            self._w += self._alpha * np.dot(X_train.T,y_bias)/sample_num
            self._b += self._alpha * np.sum(y_bias)/sample_num

    def predict(self, X_test):
        return self._w * X_test + self._b

    # 画出样本散点图以及使用模型预测的线条
    def plotFigure(self, X_test, y_test):
        # 样本散点对比图
        plt.scatter(X_test, y_test, c='r', label="samples", linewidths=0.4)
        plt.scatter(X_test, self._w * X_test + self._b, c='g', label="predict")

        # 模型预测图
        x1_min = self.X_source.min()
        x1_max = self.X_source.max()
        X_predict = np.arange(x1_min, x1_max, step=0.01)
        plt.legend(loc='upper left')

        plt.plot(X_predict, self._w * X_predict + self._b)
        plt.show()

    def store_model(self, filename):
        import pickle
        with open(filename, 'wb') as file:  
            w = [self._w, self._b]
            pickle.dump(w, file)
