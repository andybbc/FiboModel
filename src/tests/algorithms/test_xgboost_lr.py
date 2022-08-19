import xgboost as xgb
from sklearn.datasets import load_svmlight_file
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_curve, auc, roc_auc_score
from sklearn.externals import joblib
import numpy as np
from scipy.sparse import hstack
from sklearn.preprocessing.data import OneHotEncoder




# https://blog.csdn.net/dengxing1234/article/details/73739836








def xgboost_lr_train(libsvmFileNameInitial):

    # load样本数据
    X_all, y_all = load_svmlight_file(libsvmFileNameInitial)
    print(X_all)
    print(type(X_all)) # <class 'scipy.sparse.csr.csr_matrix'>
    print("=" * 10)
    print(y_all)
    print(type(y_all))

    # 训练/测试数据分割
    X_train, X_test, y_train, y_test = train_test_split(X_all, y_all, test_size=0.3, random_state=42)

    # 定义xgb模型
    xgboost = xgb.XGBClassifier(nthread=4,           # 用4个cpu进行计算
                                learning_rate=0.08,  # 学习率，控制每次迭代更新权重时的步长，默认0.3。,值越小训练越慢,0.01-0.2
                                n_estimators=50,     # 总共迭代的次数，即决策树的个数
                                max_depth=5,         # 树的深度，默认值为6，典型值3-10。值越大，越容易过拟合；值越小，越容易欠拟合。
                                gamma=0,             # 惩罚项系数，指定节点分裂所需的最小损失函数下降值。
                                subsample=0.9,       # 训练每棵树时，使用的数据占全部训练集的比例。默认值为1，典型值为0.5-1
                                colsample_bytree=0.5  # 训练每棵树时，使用的特征占全部特征的比例。默认值为1，典型值为0.5-1。
                                )
    # 训练xgb学习
    xgboost.fit(X_train, y_train)

    # 预测xgb及AUC评测
    y_pred_test = xgboost.predict_proba(X_test)[:, 1]
    xgb_test_auc = roc_auc_score(y_test, y_pred_test)
    print('xgboost test auc: %.5f' % xgb_test_auc)   # xgboost test auc: 1.00000

    # xgboost编码原有特征
    X_train_leaves = xgboost.apply(X_train)
    X_test_leaves = xgboost.apply(X_test)


    # 合并编码后的训练数据和测试数据
    All_leaves = np.concatenate((X_train_leaves, X_test_leaves), axis=0)
    All_leaves = All_leaves.astype(np.int32)

    # 对所有特征进行ont-hot编码
    xgbenc = OneHotEncoder()
    X_trans = xgbenc.fit_transform(All_leaves)

    (train_rows, cols) = X_train_leaves.shape

    # 定义LR模型
    lr = LogisticRegression()
    # lr对xgboost特征编码后的样本模型训练
    lr.fit(X_trans[:train_rows, :], y_train)
    # 预测及AUC评测
    y_pred_xgblr1 = lr.predict_proba(X_trans[train_rows:, :])[:, 1]
    xgb_lr_auc1 = roc_auc_score(y_test, y_pred_xgblr1)
    print('基于Xgb特征编码后的LR AUC: %.5f' % xgb_lr_auc1)  # 基于Xgb特征编码后的LR AUC: 1.00000

    # 定义LR模型
    lr = LogisticRegression(n_jobs=-1)
    # 组合特征
    X_train_ext = hstack([X_trans[:train_rows, :], X_train])
    X_test_ext = hstack([X_trans[train_rows:, :], X_test])

    # lr对组合特征的样本模型训练
    lr.fit(X_train_ext, y_train)

    # 预测及AUC评测
    y_pred_xgblr2 = lr.predict_proba(X_test_ext)[:, 1]
    xgb_lr_auc2 = roc_auc_score(y_test, y_pred_xgblr2)
    print('基于组合特征的LR AUC: %.5f' % xgb_lr_auc2)  # 基于组合特征的LR AUC: 1.00000


if __name__ == '__main__':
    xgboost_lr_train("../data/sample_libsvm_data.txt")