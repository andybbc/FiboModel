# %%

##进行xgboost的训练
import warnings

warnings.filterwarnings('ignore')

import gc
import csv
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import OneHotEncoder, LabelEncoder
import xgboost as xgb
from sklearn import metrics

from sklearn.externals import joblib

# %%

file_train = './out_put/encode_data_train.csv'
file_vali = './out_put/encode_data_vali.csv'
file_test = './out_put/encode_data_test.csv'

df_train = pd.read_csv(file_train, index_col=0)
df_vali = pd.read_csv(file_vali, index_col=0)
df_test = pd.read_csv(file_test, index_col=0)

# %%

##数据准备
y_train = df_train['click']
x_train = df_train.iloc[:, 1:]  # 从第二个开始往又所有
print('=' * 10)
print('''x_train=============''')
print(x_train)  # [559999 rows x 21 columns]
print(x_train.shape)
print('''y_train=============''')
print(y_train)
print(y_train.shape)
print('=' * 10)

y_vali = df_vali['click']
x_vali = df_vali.iloc[:, 1:]

y_test = df_test['click']
x_test = df_test.iloc[:, 1:]

x_test.to_csv('./out_put/x_test.csv', header=True, index=True)
y_test.to_csv('./out_put/y_test.csv', header=True, index=True)

# %%

##进行xgboost拟合
begin_time = time.time()
print(f'Begin Time : {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(begin_time))}')

##受限于机器的资源，这里就不做gridsearch调参了，直接凑合着来(按最小资源消耗来设置参数)
model = xgb.XGBClassifier(learning_rate=0.1  # 学习率，过大收敛不了，小了收敛慢
                          , n_estimators=10
                          , max_depth=3  # 构建树的深度，越大越容易过拟合，可以用CV函数来进行调优
                          , scale_pos_weight=1 # 正样本的权重，在二分类任务中，当正负样本比例失衡时，设置正样本的权重，模型效果更好。例如，当正负样本比例为1:10时，scale_pos_weight=10。
                          , min_child_weight=1  # 叶子里面h的和，h就是二阶导不清楚的看看xgboost原理，该参数越小越容易过拟合
                          , gamma=0  # 树的叶子节点上作进一步分区所需的最小损失减少,越大越保守，一般0.1、0.2这样子
                          , subsample=1  # 随机采样训练样本 训练实例的子采样比，典型值的范围在0.5-0.9之间。
                          , colsample_bylevel=1  # 生成树时进行的列采样 同subsample，一般在0.5-0.9
                          , objective='binary:logistic'  # 二分类的问题,概率
                          , n_jobs=4  # 并行线程数
                          , seed=100
                          , nthread=4  # 使用4个cpu进行计算
                          )

eval_set = [(x_vali, y_vali)]
# 原始的
model.fit(x_train, y_train, eval_metric="auc", eval_set=eval_set, early_stopping_rounds=10)
# model.fit(x_train, y_train)


end_time = time.time()
print(f'End Time : {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(end_time))}')

# %%

##保存xgb的model
joblib.dump(model, './model/xgb_model.pkl')
del model

model = joblib.load('./model/xgb_model.pkl')
# %%

# 我们来拿到xgb的叶子节点的特征
##进行xgboost拟合
begin_time = time.time()
print(f'Begin Time : {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(begin_time))}')

##apply函数返回的是叶子索引
x_train_leaves = model.apply(x_train).astype(np.int32)
x_test_leaves = model.apply(x_test).astype(np.int32)
print(" = " * 10)
print(type(x_train_leaves))  # <class 'numpy.ndarray'>
print(x_train_leaves.shape)  # (559999, 10)
print(x_train_leaves)
print(" = " * 10)
# 使用numpy的concatenate来拼接数组，并生成全局的onehot，单一使用train的可能会漏掉编码，test验证的时候出问题
x_leaves = np.concatenate((x_train_leaves, x_test_leaves), axis=0)  # axis=0二维纵向拼接,union
print(x_leaves)

print(f'Transform xgb leaves shape: {x_leaves.shape}')  # (859999, 10)

xgb_onehotcoder = OneHotEncoder()
xgb_onehotcoder.fit(x_leaves)


x_train_lr = xgb_onehotcoder.transform(x_train_leaves).toarray()  # 转成one-hot编码
x_test_lr = xgb_onehotcoder.transform(x_test_leaves).toarray()  # 转成one-hot编码
print(f'Transform xgb x_train_lr shape: {x_train_lr.shape}')  # (559999, 80)
print(f'Transform xgb x_test_lr shape: {x_test_lr.shape}')  # (300000, 80)

end_time = time.time()
print(f'End Time : {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(end_time))}')

# %%

# ##机器资源较小，进行部分变量内存回收
# del df_train, df_vali, df_test, x_vali, x_train_leaves, x_test_leaves, x_leaves, xgb_onehotcoder
# gc.collect()

# %%

# np_train_lr = np.hstack((np.array(np.mat(y_train).transpose()),x_train_lr))
# np.savetxt("./out_put/encode_data_train_lr.csv", np_train_lr, delimiter=',')

# %%

# del np_train_lr
# gc.collect()

# %%

# np_test_lr = np.hstack((np.array(np.mat(y_test).transpose()),x_test_lr))
# np.savetxt("./out_put/encode_data_test_lr.csv", np_test_lr, delimiter=',')

# %%

# del np_test_lr
# gc.collect()

# %%

## hstack 进行one特征与原始特征的拼接
x_train_lr2 = np.hstack((x_train_lr, x_train.values))  # :在水平方向上平铺,横向
print(f'Transform xgb x_train_lr2 shape: {x_train_lr2.shape}')  # (559999, 101)

# np_train_lr2 = np.hstack((np.array(np.mat(y_train).transpose()),x_train_lr2))
# np.savetxt("./out_put/encode_data_train_lr2.csv", np_train_lr2, delimiter=',')

# %%

# del x_train,x_train_lr,x_train_lr2,np_train_lr2
# gc.collect()

# %%

x_test_lr2 = np.hstack((x_test_lr, x_test.values))
print(f'Transform xgb x_test_lr2 shape: {x_test_lr2.shape}')  # (300000, 101)

# np_test_lr2 = np.hstack((np.array(np.mat(y_test).transpose()),x_test_lr2))
# np.savetxt("./out_put/encode_data_test_lr2.csv", np_test_lr2, delimiter=',')

# %%

##回收部分资源，资源不够了
del df_train, df_vali, df_test, x_vali, x_train_leaves, x_test_leaves, x_leaves, xgb_onehotcoder
gc.collect()


# %%

###灌入到LR中
begin_time = time.time()
print(f'Begin Time : {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(begin_time))}')

lr_model = LogisticRegression()
lr_model.fit(x_train_lr, y_train)

lr_model2 = LogisticRegression()
lr_model2.fit(x_train_lr2, y_train)

joblib.dump(lr_model, './model/lr_model.pkl')
joblib.dump(lr_model2, './model/lr_model2.pkl')

end_time = time.time()
print(f'End Time : {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(end_time))}')


# %%

##效果输出函数
def func_print_score(x_data, y_data, data_type, model_x):
    y_pred = model_x.predict(x_data)

    print(f'==============({data_type})===================')
    confusion = metrics.confusion_matrix(y_data, y_pred)
    print(confusion)

    print('------------------------')
    auc = metrics.roc_auc_score(y_data, y_pred)
    print(f'AUC: {auc}')

    print('------------------------')
    accuracy = metrics.accuracy_score(y_data, y_pred)
    print(f'Accuracy: {accuracy}')

    print('------------------------')
    aupr = metrics.average_precision_score(y_data, y_pred)
    print(f'AUPR: {aupr}')

    print('------------------------')
    report = metrics.classification_report(y_data, y_pred)
    print(report)

    print('=============================================')


# %%

func_print_score(x_test, y_test, 'testdata-xgb', model)
func_print_score(x_test_lr, y_test, 'testdata-xgb-lr', lr_model)  # one-hot编码后的
func_print_score(x_test_lr2, y_test, 'testdata-xgb-lr2', lr_model2)  # 合并后的

# %%

del x_train, y_train, x_train_lr, x_train_lr2
gc.collect()

# %%

##测试数据的PR曲线
# model.predict_proba 返回预测属于某标签的概率 https://www.cnblogs.com/mrtop/p/10309083.html
probas_xgb = model.predict_proba(x_test)
np.savetxt("./out_put/probas_xgb.txt", probas_xgb, delimiter=",")  # 保存结果看看

probas_lr = lr_model.predict_proba(x_test_lr)
probas_lr2 = lr_model2.predict_proba(x_test_lr2)
print("===================xgb_predict===================")
print(model.predict(x_test))  # [0 0 0 ... 0 0 0]
print(probas_xgb)  # [[0.69095546 0.30904454]  [0.63493407 0.36506596]  [0.76500106 0.23499897]  [0.6865822  0.3134178 ]]
print(type(probas_xgb))  # <class 'numpy.ndarray'>
print("-" * 10)

print("===================probas_lr===================")
print(probas_lr)  # [[0.69095546 0.30904454]  [0.63493407 0.36506596]  [0.76500106 0.23499897]  [0.6865822  0.3134178 ]]
print("-" * 10)

print("===================probas_lr2===================")
print(probas_lr2)  # [[0.69095546 0.30904454]  [0.63493407 0.36506596]  [0.76500106 0.23499897]  [0.6865822  0.3134178 ]]
print("-" * 10)

# %%

##precision_recall_curve 函数
precision_xgb, recall_xgb, thresholds_xgb = metrics.precision_recall_curve(y_test, probas_xgb[:, 1])
precision_lr, recall_lr, thresholds_lr = metrics.precision_recall_curve(y_test, probas_lr[:, 1])
precision_lr2, recall_lr2, thresholds_lr2 = metrics.precision_recall_curve(y_test, probas_lr2[:, 1])

# %%

plt.figure(figsize=(8, 6))

plt.plot(recall_xgb, precision_xgb, label='xgb', alpha=0.8, color='red')
plt.plot(recall_lr, precision_lr, label='xgg-lr', alpha=0.8, color='blue')
plt.plot(recall_lr2, precision_lr2, label='xgb-lr2', alpha=0.8, color='green')

plt.plot([0, 1], [0, 1], 'k--')

# 图例打印
plt.legend(bbox_to_anchor=(1.05, 0), loc=3, borderaxespad=1)

plt.xlim([-0.05, 1.05])
plt.ylim([-0.05, 1.05])

plt.xlabel('Recall Rate')
plt.ylabel('Precision Rate')
plt.title('PR Curve')

# %%
