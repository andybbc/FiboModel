# -*- coding:utf-8 -*-

import numpy as np
from evaluate.auc import AUC
from model.base import Base


def sigmoid1(x):
    return 1 / (1 + np.exp(-x))


def lossFunc1(X, y, w):
    # 计算预估值
    h = X.dot(w)

    y_pred = sigmoid1(h)

    return X.T.dot(y - y_pred)


def sigmoid2(x):
    return np.exp(x) / (1 + np.exp(x))


def lossFunc2(X, y, w):
    # 计算预估值
    h = X.dot(w)

    y_pred = sigmoid2(h)

    return X.T.dot(y - y_pred)


class LogisticRegression(Base):
    '''
    逻辑回归分析类
    参数：
        alpha:  迭代步长
        n_iter: 迭代次数
    使用示例：
        lr = LogisticRegression()        # 实例化类
        lr.initialPara(N)                # 根据特征个数初始化预估参数
        lr.fit(X_train, y_train)         # 训练模型
        lr.predict(X_test)               # 预测训练数据
        lr.score(X_test, y_test)         # 计算准确率
        lr.plotFigure()                  # 用于画出样本散点图与预测模型
    '''

    def __init__(self, dic_config={}):
        Base.__init__(self, dic_config)
        self._alpha = dic_config.get('alpha', 0.02)      # 步长
        self._n_iter = dic_config.get('n_iter', 200)     # 梯度训练迭代次数

    # 初始化模型参数矩阵
    def initialPara(self, n_features=1, b_start=0):
        # 权值向量中的权值大小范围 [-1/sqrt(N)， 1/sqrt(N)]
        # 矩阵大小 (N, 1)
        limit = np.sqrt(1 / n_features)
        _w = np.random.uniform(-limit, limit, (n_features, 1))

        # 矩阵中加入偏置值 b (索引在 0 位)
        self._w = np.insert(_w, 0, b_start, axis=0)

    # 训练模型
    def fit(self, X_train, y_train):
        # 保存原始数据
        self.X_source = X_train.copy()
        self.y_source = y_train.copy()

        # 获取训练样本、特征数据
        sample_num = X_train.shape[0]
        feature_num = X_train.shape[1]

        # 初始化w，b
        self.initialPara(feature_num)

        # 对应偏置项，在样本数据集首位增加一列特征值，值为 1(不影响偏置值)
        X_train = np.insert(X_train, 0, 1, axis=1)
        y_train = np.reshape(y_train, (sample_num, 1))

        # 开始训练迭代
        for _ in range(self._n_iter):

            # 方法一：
            # 调用预估算法，计算损失修正矩阵
            w_grade = lossFunc1(X_train, y_train, self._w)

            # 梯度上升
            self._w += self._alpha * w_grade

            # 方法二：
            # 遍历所有样本，随机梯度上升
            # for n in range(sample_num):
            #     w_grade = lossFunc2(X_train, y_train, self._w)

            # 梯度上升
            #     self._w += self._alpha * w_grade

    def predict(self, X_test, y_test):
        X = np.insert(X_test, 0, 1, axis=1)

        # 二项逻辑斯蒂回归模型；np.round四舍五入,小于0.5等于0,大于0.5等于1
        y_pred = np.round(sigmoid1(X.dot(self._w)))

        y_pred = np.reshape(y_pred, y_test.shape)
        return y_pred.astype(int)

    def score(self, X_test, y_test):
        y_pred = self.predict(X_test, y_test)
        print(y_pred)
        print(y_test)

        # 错误率
        errcnt = 0
        for n in range(X_test.shape[0]):
            if y_pred.T[n] != y_test.T[n]:
                errcnt += 1

        # 返回正确率
        return 1 - errcnt / X_test.shape[0]

    def score1(self, X_test, y_test):
        X = np.insert(X_test, 0, 1, axis=1)
        y_pred = sigmoid1(X.dot(self._w))
        y_pred = np.reshape(y_pred, y_test.shape)
        auc = AUC(y_test, y_pred)
        return auc.calculate1()

    def score2(self, X_test, y_test):
        X = np.insert(X_test, 0, 1, axis=1)
        y_pred = sigmoid1(X.dot(self._w))
        y_pred = np.reshape(y_pred, y_test.shape)
        auc = AUC(y_test, y_pred)
        return auc.calculate2()

    def storeModel(self, filename):
        import pickle
        with open(filename, 'wb') as file:
            pickle.dump(self._w, file)
