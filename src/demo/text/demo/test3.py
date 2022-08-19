"""
数据格式有问题，未跑通
https://www.jianshu.com/p/392b6ef4656b
2019年6月15日跑通
"""
import xgboost_test_package as xgb
import numpy as np
import random
import math
from sklearn.model_selection import RandomizedSearchCV

# 首先随机生成数据
n_group = 2
n_choice = 3
X_train = np.random.uniform(0, 100, [n_group * n_choice, 2])
y_train = np.array([np.random.choice([0, 1, 2], 3, False) for i in range(n_group)]).flatten()
X_test = np.random.uniform(0, 100, [n_group * n_choice, 2])
y_test = np.array([np.random.choice([0, 1, 2], 3, False) for i in range(n_group)]).flatten()

from sklearn.metrics import make_scorer


def _to_list(x):
    if isinstance(x, list):
        return x
    return [x]


def ndcg(y_true, y_pred, k=20, rel_threshold=0):
    if k <= 0:
        return 0
    y_true = _to_list(np.squeeze(y_true).tolist())
    y_pred = _to_list(np.squeeze(y_pred).tolist())
    c = list(zip(y_true, y_pred))
    random.shuffle(c)
    c_g = sorted(c, key=lambda x: x[0], reverse=True)
    c_p = sorted(c, key=lambda x: x[1], reverse=True)
    idcg = 0
    ndcg = 0
    for i, (g, p) in enumerate(c_g):
        if i >= k:
            break
        if g > rel_threshold:
            idcg += (math.pow(2, g) - 1) / math.log(2 + i)
    for i, (g, p) in enumerate(c_p):
        if i >= k:
            break
        if g > rel_threshold:
            ndcg += (math.pow(2, g) - 1) / math.log(2 + i)
    if idcg == 0:
        return 0
    else:
        return ndcg / idcg

model = xgb.XGBClassifier(
    nthread=20,
    learn_rate=0.1,
    max_depth=15,
    min_child_weight=2,
    subsample=0.8,
    colsample_bytree=1,
    objective='rank:pairwise',
    n_estimators=300,
    gamma=0,
    reg_alpha=0,
    reg_lambda=1,
    max_delta_step=0,
    scale_pos_weight=1
)
watchlist = [(X_train, y_train), (X_test, y_test)]
model.fit(X_train, y_train, eval_set=watchlist, eval_metric='mlogloss')

"""接下来进行调参"""
from sklearn.metrics import make_scorer

def _to_list(x):
    if isinstance(x, list):
        return x
    return [x]

def ndcg(y_true, y_pred, k=20, rel_threshold=0):
    if k <= 0:
        return 0
    y_true = _to_list(np.squeeze(y_true).tolist())
    y_pred = _to_list(np.squeeze(y_pred).tolist())
    c = list(zip(y_true, y_pred))
    random.shuffle(c)
    c_g = sorted(c, key=lambda x: x[0], reverse=True)
    c_p = sorted(c, key=lambda x: x[1], reverse=True)
    idcg = 0
    ndcg = 0
    for i, (g, p) in enumerate(c_g):
        if i >= k:
            break
        if g > rel_threshold:
            idcg += (math.pow(2, g) - 1) / math.log(2 + i)
    for i, (g, p) in enumerate(c_p):
        if i >= k:
            break
        if g > rel_threshold:
            ndcg += (math.pow(2, g) - 1) / math.log(2 + i)
    if idcg == 0:
        return 0
    else:
        return ndcg / idcg

ndcg_score = make_scorer(ndcg)
parameters = {
    'max_depth': [4, 6, 8, 10, 15],
    'learn_rate': [0.01, 0.02, 0.05, 0.1, 0.15],
    'n_estimators': [100, 300, 500, 1000],
    'min_child_weight': [0, 2, 5, 10, 20],
    'subsample': [0.6, 0.7, 0.8, 0.85, 0.95],
    'colsample_bytree': [0.5, 0.6, 0.7, 0.8, 0.9]
}
model = xgb.sklearn.XGBClassifier(
    nthread=20,
    silent=False,
    learn_rate=0.1,
    max_depth=6,
    min_child_weight=3,
    subsample=0.7,
    colsample_bytree=0.7,
    objective='binary:logistic',
    n_estimators=10
)
#接下来的这个参数很重要 cv是将训练集分为多少个Fold
gsearch = RandomizedSearchCV(model, param_distributions=parameters, scoring=ndcg_score, cv=2)
print('gridsearchcv fit begin...')
gsearch.fit(X_train, y_train)
print('Best score: {}'.format(gsearch.best_score_))
print('Best parameters set: {}'.format(gsearch.best_estimator_.get_params()))
