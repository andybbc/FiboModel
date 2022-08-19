# -*- coding:utf-8 -*-

import numpy as np
from collections import Counter


class KNearestNeighbor:
    '''
    线性回归类
    参数：
        num_folds: 迭代步长
        k_choices: 迭代次数
    使用示例：
        knn = KNearestNeighbor()          # 实例化类
        knn.initialPara(w_start, b_start) # 初始化预估参数
        knn.fit(X_train,y_train)          # 训练模型
        y_predict = knn.predict(X_test)   # 预测训练数据
        knn.plotFigure()                  # 用于画出样本散点图与预测模型
    '''
    def __init__(self, dic_config={}):
        self._num_folds = dic_config.get('num_folds', 5)
        self._k_choices = dic_config.get('k_choices', [1, 3, 5, 8, 10, 12, 15, 20])

    # 初始化模型参数
    def initialPara(self, X, y):
        self.X_train = X
        self.y_train = y

    def compute_distances(self, X):
        num_test = X.shape[0]
        num_train = self.X_train.shape[0]
        dists = np.zeros((num_test, num_train)) 

        M = np.dot(X, self.X_train.T)
        te = np.square(X).sum(axis=1)
        tr = np.square(self.X_train).sum(axis=1)
        dists = np.sqrt(-2 * M + tr + np.matrix(te).T)        
        return dists

    def fit(self, X_train, y_train):
        X_train_folds = []
        y_train_folds = []

        X_train_folds = np.array_split(X_train, self._num_folds)
        y_train_folds = np.array_split(y_train,  self._num_folds)

        k_to_accuracies = {}        
        for k in  self._k_choices:            
            for fold in range( self._num_folds): 
                validation_X_test = X_train_folds[fold]
                validation_y_test = y_train_folds[fold]
                temp_X_train = np.concatenate(X_train_folds[:fold] + X_train_folds[fold + 1:])
                temp_y_train = np.concatenate(y_train_folds[:fold] + y_train_folds[fold + 1:])


                self.initialPara(temp_X_train, temp_y_train )

                temp_dists = self.compute_distances(validation_X_test)
                temp_y_test_pred = self.predict(temp_dists, k=k)
                temp_y_test_pred = temp_y_test_pred.reshape((-1, 1))                #Checking accuracies
                num_correct = np.sum(temp_y_test_pred == validation_y_test)
                num_test = validation_X_test.shape[0]
                accuracy = float(num_correct) / num_test
                k_to_accuracies[k] = k_to_accuracies.get(k,[]) + [accuracy]        # Print out the computed accuracies
        
        for k in sorted(k_to_accuracies):            
            for accuracy in k_to_accuracies[k]:
                print('k = %d, accuracy = %f' % (k, accuracy))

        accuracies_mean = np.array([np.mean(v) for k,v in sorted(k_to_accuracies.items())])
        self.best_k = self._k_choices[np.argmax(accuracies_mean)]
        print('最佳k值为{}'.format(self.best_k))

    def predict(self, dists, k=1):
        num_test = dists.shape[0]
        y_pred = np.zeros(num_test)         
        for i in range(num_test):
            closest_y = []
            labels = self.y_train[np.argsort(dists[i, :])].flatten()
            closest_y = labels[0:k]

            c = Counter(closest_y)
            y_pred[i] = c.most_common(1)[0][0]        
        return y_pred
