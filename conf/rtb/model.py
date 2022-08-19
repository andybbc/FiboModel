# xgb.XGBClassifier参数

CONFIG = {
    'xgboost_lr': {
        # 有效的案例,最优的案例
        # 'params': {
        #     "learning_rate": 0.1,  # 学习率，过大收敛不了，小了收敛慢
        #     "n_estimators": 200,
        #     "max_depth": 6,  # 构建树的深度，越大越容易过拟合，可以用CV函数来进行调优
        #     "scale_pos_weight": 2.5,  # 正样本的权重，在二分类任务中，当正负样本比例失衡时，设置正样本的权重，模型效果更好。例如，当正负样>本比例为1:10时，scale_pos_weight=10。
        #     "min_child_weight": 0.9,  # 叶子里面h的和，h就是二阶导不清楚的看看xgboost原理，该参数越小越容易过拟合
        #     "gamma": 0.1,  # 树的叶子节点上作进一步分区所需的最小损失减少,越大越保守，一般0.1、0.2这样子
        #     "subsample": 0.9,  # 随机采样训练样本 训练实例的子采样比，典型值的范围在0.5-0.9之间。
        #     "colsample_bylevel": 0.5,  # 生成树时进行的列采样 同subsample，一般在0.5-0.9
        #     "objective": 'binary:logistic',  # 二分类的问题,概率
        #     "n_jobs": 4,  # 并行线程数
        #     "seed": 27,
        #     "nthread": -1  # 使用4个cpu进行计算
        # },


        # 20210526测试
        # 原始数据正样本+3
        # === test auc: %s === 0.7735774646401807
        # left : real     right: pred
        # ============predict5===============
        # ((0,0),249638,0.499276)
        # ((0,1),123298,0.246596)
        # ((1,1),93992,0.187984)
        # ((1,0),33072,0.066144)
        # 'params': {
        #     "learning_rate": 0.9,  # 学习率，过大收敛不了，小了收敛慢
        #     "n_estimators": 1500,
        #     "max_depth": 12,  # 构建树的深度，越大越容易过拟合，可以用CV函数来进行调优
        #     "scale_pos_weight": 1,  # 正样本的权重，在二分类任务中，当正负样本比例失衡时，设置正样本的权重，模型效果更好。例如，当正负样>本比例为1:10时，scale_pos_weight=10。
        #     # "min_child_weight": 0.9,  # 叶子里面h的和，h就是二阶导不清楚的看看xgboost原理，该参数越小越容易过拟合
        #     "min_child_weight": 100,  # 叶子里面h的和，h就是二阶导不清楚的看看xgboost原理，该参数越小越容易过拟合
        #     "gamma": 0.2,   # 树的叶子节点上作进一步分区所需的最小损失减少,越大越保守，一般0.1、0.2这样子
        #     "subsample": 0.8,  # 随机采样训练样本 训练实例的子采样比，典型值的范围在0.5-0.9之间。
        #     "colsample_bylevel": 0.9,  # 生成树时进行的列采样 同subsample，一般在0.5-0.9
        #     "objective": 'binary:logistic',  # 二分类的问题,概率
        #     "n_jobs": 4,  # 并行线程数
        #     "seed": 27,
        #     "nthread": -1,  # 使用4个cpu进行计算
        #     "max_delta_step": 10  # 新加参数 # https://posts.careerengine.us/p/5d60ad6a50812d6fe01e7413
        # },  # https://zhuanlan.zhihu.com/p/139154630 base_score 样本不平衡参数


        # 比上面稍微好点:,样本还是1 * 3
        # === test auc: %s === 0.786866236938174
        # left : real     right: pred
        # ============predict5===============
        # ((0,0),252805,0.50561)
        # ((0,1),119456,0.238912)
        # ((1,1),96498,0.192996)
        # ((1,0),31241,0.062482)
        # 'params': {
        #     "learning_rate": 0.9,  # 学习率，过大收敛不了，小了收敛慢
        #     "n_estimators": 2000,
        #     "max_depth": 12,  # 构建树的深度，越大越容易过拟合，可以用CV函数来进行调优
        #     "scale_pos_weight": 1,  # 正样本的权重，在二分类任务中，当正负样本比例失衡时，设置正样本的权重，模型效果更好。例如，当正负样>本比例为1:10时，scale_pos_weight=10。
        #     # "min_child_weight": 0.9,  # 叶子里面h的和，h就是二阶导不清楚的看看xgboost原理，该参数越小越容易过拟合
        #     "min_child_weight": 100,  # 叶子里面h的和，h就是二阶导不清楚的看看xgboost原理，该参数越小越容易过拟合
        #     "gamma": 0.2,   # 树的叶子节点上作进一步分区所需的最小损失减少,越大越保守，一般0.1、0.2这样子
        #     "subsample": 0.8,  # 随机采样训练样本 训练实例的子采样比，典型值的范围在0.5-0.9之间。
        #     "colsample_bylevel": 0.9,  # 生成树时进行的列采样 同subsample，一般在0.5-0.9
        #     "objective": 'binary:logistic',  # 二分类的问题,概率
        #     "n_jobs": 4,  # 并行线程数
        #     "seed": 27,
        #     "nthread": -1,  # 使用4个cpu进行计算
        #     "max_delta_step": 5  # 新加参数 # https://posts.careerengine.us/p/5d60ad6a50812d6fe01e7413
        # },  # https://zhuanlan.zhihu.com/p/139154630 base_score 样本不平衡参数

        # 复制3:1
        # === test auc: %s === 0.806970154810418
        # left : real     right: pred
        # ============predict5===============
        # ((0,0),259139,0.518278)
        # ((0,1),113122,0.226244)
        # ((1,1),99019,0.198038)
        # ((1,0),28720,0.05744)
        # 'params': {
        #     "learning_rate": 1,  # 学习率，过大收敛不了，小了收敛慢
        #     "n_estimators": 3000,
        #     "max_depth": 12,  # 构建树的深度，越大越容易过拟合，可以用CV函数来进行调优
        #     "scale_pos_weight": 1,  # 正样本的权重，在二分类任务中，当正负样本比例失衡时，设置正样本的权重，模型效果更好。例如，当正负样>本比例为1:10时，scale_pos_weight=10。
        #     # "min_child_weight": 0.9,  # 叶子里面h的和，h就是二阶导不清楚的看看xgboost原理，该参数越小越容易过拟合
        #     "min_child_weight": 100,  # 叶子里面h的和，h就是二阶导不清楚的看看xgboost原理，该参数越小越容易过拟合
        #     "gamma": 0.2,  # 树的叶子节点上作进一步分区所需的最小损失减少,越大越保守，一般0.1、0.2这样子
        #     "subsample": 0.8,  # 随机采样训练样本 训练实例的子采样比，典型值的范围在0.5-0.9之间。
        #     "colsample_bylevel": 0.9,  # 生成树时进行的列采样 同subsample，一般在0.5-0.9
        #     "objective": 'binary:logistic',  # 二分类的问题,概率
        #     "n_jobs": 4,  # 并行线程数
        #     "seed": 27,
        #     "nthread": -1,  # 使用4个cpu进行计算
        #     "max_delta_step": 4  # 新加参数 # https://posts.careerengine.us/p/5d60ad6a50812d6fe01e7413
        # },  # https://zhuanlan.zhihu.com/p/139154630 base_score 样本不平衡参数

        # === test auc: %s === 0.7193555601284991
        # left : real     right: pred
        # ============predict5===============
        # ((0,0),185428,0.30345500248749707)
        # ((0,1),115588,0.18916105888821974)
        # ((1,1),222834,0.36467034117985914)
        # ((1,0),87206,0.14271359744442408)
        #
        #
        # TPR(???????????(???,????)):0.7187266159205263
        # FPR(???????????(???)):0.383992877455019
        # TNR(???????????(???)):0.616007122544981
        # FNR(???????????(???/???,????)):0.2812733840794736
        'params': {
            "learning_rate": 1,  # 学习率，过大收敛不了，小了收敛慢
            "n_estimators": 10000,
            "max_depth": 12,  # 构建树的深度，越大越容易过拟合，可以用CV函数来进行调优
            "scale_pos_weight": 1,  # 正样本的权重，在二分类任务中，当正负样本比例失衡时，设置正样本的权重，模型效果更好。例如，当正负样>本比例为1:10时，scale_pos_weight=10。
            # "min_child_weight": 0.9,  # 叶子里面h的和，h就是二阶导不清楚的看看xgboost原理，该参数越小越容易过拟合
            "min_child_weight": 100,  # 叶子里面h的和，h就是二阶导不清楚的看看xgboost原理，该参数越小越容易过拟合
            "gamma": 0.2,  # 树的叶子节点上作进一步分区所需的最小损失减少,越大越保守，一般0.1、0.2这样子
            "subsample": 0.8,  # 随机采样训练样本 训练实例的子采样比，典型值的范围在0.5-0.9之间。
            "colsample_bylevel": 0.9,  # 生成树时进行的列采样 同subsample，一般在0.5-0.9
            "objective": 'binary:logistic',  # 二分类的问题,概率
            "n_jobs": 4,  # 并行线程数
            "seed": 27,
            "nthread": -1,  # 使用4个cpu进行计算
            "max_delta_step": 15  # 新加参数 # https://posts.careerengine.us/p/5d60ad6a50812d6fe01e7413
        },  # https://zhuanlan.zhihu.com/p/139154630 base_score 样本不平衡参数

        'xgb_fit_params': {
            "early_stopping_rounds": 100
        }
    },
    "deepfm": {
        "params": {
            "task": "binary"
        },
        "compile_params": {
            "optimizer": "adam",
            "loss": "binary_crossentropy",
            "metrics": ['binary_crossentropy']
        },
        "fit_params": {
            "batch_size": 256,
            "epochs": 20,
            "verbose": 2,
            "validation": 0.2,
        },
        "predict_params": {
            "batch_size": 256
        }
    },
    "xdeepfm": {
        "params": {
            "task": "binary",
            'dnn_hidden_units': (8,),
            "cin_layer_size": (),
            'cin_split_half': True,
            'cin_activation': 'linear',
            'dnn_dropout': 0.5

        },
        "compile_params": {
            "optimizer": "adam",
            "loss": "binary_crossentropy",
            "metrics": ['binary_crossentropy']
        },
        "fit_params": {
            "batch_size": 256,
            "epochs": 20,
            "verbose": 2,
            "validation": 0.2,
            "validation_split": 0.5
        },
        "predict_params": {
            "batch_size": 256
        }
    },
}
