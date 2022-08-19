params = {
    'booster': 'gbtree',
    'objective': 'multi:softmax',
    # 'objective': 'multi:softprob',   #Multiclassification probability
    'num_class': 3,
    'eval_metric': 'mlogloss',
    'gamma': 0.1,
    'max_depth': 8,
    'alpha': 0,
    'lambda': 0,
    'subsample': 0.7,
    'colsample_bytree': 0.5,
    'min_child_weight': 3,
    'silent': 0,
    'eta': 0.03,
    'nthread': -1,
    'missing': 1,
    'seed': 2019,
}

# 训练数据参数
train_params = {
    'test_size': 0.25,  # 分割抽样比例,训练
    'random_state': 100,
    'verbose_eval': 20,  # 训练显示间隔
    'early_stopping_rounds': 50,  # 训练超过多少次没有优化就停止,
    'num_round': 100
}

k_fold_params = {
    'n_splits': 5,
    'shuffle': True,
    'random_state': 2019
}

text_params = {'max_depth': 6,
               'eta': 0.5,
               'eval_metric': 'merror',
               'silent': 1,
               'objective': 'multi:softmax',
               'num_class': 11
               }
# text_params={
#     'booster': 'gbtree',
#     'objective': 'multi:softmax',
#     # 'objective': 'multi:softprob',   #Multiclassification probability
#     'num_class': 11,
#     'eval_metric': 'mlogloss',
#     'gamma': 0.1,
#     'max_depth': 8,
#     'alpha': 0,
#     'lambda': 0,
#     'subsample': 0.7,
#     'colsample_bytree': 0.5,
#     'min_child_weight': 3,
#     'silent': 0,
#     'eta': 0.03,
#     'nthread': -1,
#     'missing': 1,
#     'seed': 2019,
# }
