# -*- coding: utf-8 -*-
# * @author Ming_H
# * @date 2019/05/16
# * Usage: Tree methods with LR method

# https://www.icode9.com/content-4-200544.html


import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import OneHotEncoder
from sklearn.model_selection import train_test_split
from sklearn import metrics
import logging
import xgboost as xgb
import time
from sklearn.datasets import load_iris

logging.basicConfig(format='%(asctime)s : %(levelname)s: %(message)s', level=logging.INFO)


def XGBoost_LR(df_train):  # df_train [100 rows x 5 columns]
    X_train = df_train.values[:, :-1]
    print(type(X_train))  # <class 'numpy.ndarray'>
    print(X_train)  # 前4列数据
    y_train = df_train.values[:, -1]
    print(y_train)  # 第5列数据
    # X_train, X_test, y_train, y_test
    X_train_xgb, X_train_lr, y_train_xgb, y_train_lr = train_test_split(X_train,
                                                                        y_train, test_size=0.75)
    print("=" * 10)
    print(type(X_train_xgb))  # <class 'numpy.ndarray'>
    print("=" * 10)
    print("=" * 10)

    XGB = xgb.XGBClassifier(scale_pos_weight=1,
                            objective="binary:logistic",
                            eval_metric='logloss',
                            booster='gbtree',  # gbtree, gblinear or dart
                            learning_rate=0.01,  # 如同学习率
                            n_estimators=6,  # 树的个数
                            max_depth=5,  # 构建树的深度，越大越容易过拟合
                            min_child_weight=3,  # 这个参数默认是 1，是每个叶子里面 h 的和至少是多少
                            gamma=0.3,  # 树的叶子节点上作进一步分区所需的最小损失减少,越大越保守，一般0.1、0.2这样子。
                            # subsample = 0.5,                # 随机采样训练样本 训练实例的子采样比
                            # colsample_bytree = 0.8,         # 生成树时进行的列采样
                            # reg_alpha = 1,                  # L1 正则项参数
                            # reg_lambda = 4,                 # 控制模型复杂度的权重值的L2正则化项参数，参数越大，模型越不容易过拟合。
                            # max_delta_step = 0,             # 最大增量步长，我们允许每个树的权重估计。
                            # seed = 100,                     # 随机种子
                            missing=-999.0  # 为缺失值设置默认值

                            )
    XGB.fit(X_train_xgb, y_train_xgb)

    logging.info("训练集特征数据为： \n%s" % X_train_xgb)
    logging.info("训练集标签数据为： \n%s" % y_train_xgb)

    # 转化为叶子节点的特征
    res = XGB.apply(X_train_xgb, ntree_limit=0)
    print(type(res))  # <class 'numpy.ndarray'>
    logging.info("转化为叶子节点后的特征为：\n%s" % res)

    XGB_enc = OneHotEncoder()
    XGB_enc.fit(XGB.apply(X_train_xgb, ntree_limit=0))  # ntree_limit 预测时使用的树的数量

    XGB_LR = LogisticRegression(class_weight="balanced",
                                penalty='l2',
                                dual=False,
                                tol=0.001,
                                C=0.001,
                                # fit_intercept=True,
                                # intercept_scaling=1,
                                # random_state=None,
                                # solver='liblinear',   # newton-cg, lbfgs, liblinear, sag, saga}, default: liblinear.
                                # max_iter=100,
                                # multi_class='ovr',  # ovr, multinomial, auto
                                # verbose=0,
                                # warm_start=False,
                                # n_jobs=None
                                )

    XGB_LR.fit(XGB_enc.transform(XGB.apply(X_train_lr)), y_train_lr.astype('int'))

    X_predict = XGB_LR.predict_proba(XGB_enc.transform(XGB.apply(X_train)))[:, 1]
    print("=====")
    print(X_predict)
    print("=====")

    AUC_train = metrics.roc_auc_score(y_train.astype('int'), X_predict)
    logging.info("AUC of train data is %f" % AUC_train)  # AUC of train data is 1.000000


if __name__ == "__main__":
    start = time.clock()
    # 加载数据集
    iris = load_iris()
    print(iris.data)
    print('=' * 10)
    print(iris.target)
    df_data = pd.concat([pd.DataFrame(iris.data), pd.DataFrame(iris.target)], axis=1)  # axis=1 横向拼接
    print(df_data)  # [150 rows x 5 columns]
    print(type(df_data))  # <class 'pandas.core.frame.DataFrame'>
    df_data.columns = ["x1", "x2", "x3", "x4", "y"]
    df_new = df_data[df_data["y"] < 2]
    print(df_new)  # [100 rows x 5 columns]

    logging.info("Train model begine...")
    XGBoost_LR(df_new)
    end = time.clock()
    logging.info("Program over, time cost is %s" % (end - start))
