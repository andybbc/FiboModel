import sys

from nyoka import xgboost_to_pmml
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import OneHotEncoder
from sklearn_pandas import DataFrameMapper

sys.path.append("..")
import numpy as np
from model.base import Base
import xgboost as xgb

from xgboost.sklearn import XGBClassifier
from sklearn2pmml import PMMLPipeline
from sklearn2pmml import sklearn2pmml
from sklearn.pipeline import Pipeline
from xgboost import plot_importance
from matplotlib import pyplot


class XgboostRTBModel(Base):
    def __init__(self, dic_config):
        super().__init__(dic_config)
        self.dic_config = dic_config

        # self.model = xgb.XGBClassifier(  # 尝试使用sklearn的方法
        #     # self.model = XGBClassifier(
        #     learning_rate=self.dic_config['model_config']['xgboost_lr']['params']['learning_rate'],  # 学习率，过大收敛不了，小了收敛慢
        #     n_estimators=self.dic_config['model_config']['xgboost_lr']['params']['n_estimators'],
        #     max_depth=self.dic_config['model_config']['xgboost_lr']['params']['max_depth'],
        #     # 构建树的深度，越大越容易过拟合，可以用CV函数来进行调优
        #     scale_pos_weight=self.dic_config['model_config']['xgboost_lr']['params']['scale_pos_weight'],
        #     # 正样本的权重，在二分类任务中，当正负样本比例失衡时，设置正样本的权重，模型效果更好。例如，当正负样本比例为1:10时，scale_pos_weight=10。
        #     min_child_weight=self.dic_config['model_config']['xgboost_lr']['params']['min_child_weight'],
        #     # 叶子里面h的和，h就是二阶导不清楚的看看xgboost原理，该参数越小越容易过拟合
        #     gamma=self.dic_config['model_config']['xgboost_lr']['params']['gamma'],
        #     # 树的叶子节点上作进一步分区所需的最小损失减少,越大越保守，一般0.1、0.2这样子
        #     subsample=self.dic_config['model_config']['xgboost_lr']['params']['subsample'],
        #     # 随机采样训练样本 训练实例的子采样比，典型值的范围在0.5-0.9之间。
        #     colsample_bylevel=self.dic_config['model_config']['xgboost_lr']['params']['colsample_bylevel'],
        #     # 生成树时进行的列采样 同subsample，一般在0.5-0.9
        #     objective=self.dic_config['model_config']['xgboost_lr']['params']['objective'],  # 二分类的问题,概率
        #     n_jobs=self.dic_config['model_config']['xgboost_lr']['params']['n_jobs'],  # 并行线程数
        #     seed=self.dic_config['model_config']['xgboost_lr']['params']['seed'],
        #     nthread=self.dic_config['model_config']['xgboost_lr']['params']['nthread'],  # 使用4个cpu进行计算
        # )
        print(f"=====xgb_init_param:{self.dic_config['model_config']['xgboost_lr']['params']}=====")
        self.model = xgb.XGBClassifier(  # 尝试使用sklearn的方法
            **self.dic_config['model_config']['xgboost_lr']['params']
        )

    '''
    # 基于xgboost的二分类训练
    def train(self, x_train, y_train, eval_set):
        model = xgb.XGBClassifier(learning_rate=self.dic_config['model_config']['xgboost_lr']['params']['learning_rate'],  # 学习率，过大收敛不了，小了收敛慢
                                  n_estimators=self.dic_config['model_config']['xgboost_lr']['params']['n_estimators'],
                                  max_depth=self.dic_config['model_config']['xgboost_lr']['params']['max_depth'],  # 构建树的深度，越大越容易过拟合，可以用CV函数来进行调优
                                  scale_pos_weight=self.dic_config['model_config']['xgboost_lr']['params']['scale_pos_weight'],
                                  # 正样本的权重，在二分类任务中，当正负样本比例失衡时，设置正样本的权重，模型效果更好。例如，当正负样本比例为1:10时，scale_pos_weight=10。
                                  min_child_weight=self.dic_config['model_config']['xgboost_lr']['params']['min_child_weight'],  # 叶子里面h的和，h就是二阶导不清楚的看看xgboost原理，该参数越小越容易过拟合
                                  gamma=self.dic_config['model_config']['xgboost_lr']['params']['gamma'],  # 树的叶子节点上作进一步分区所需的最小损失减少,越大越保守，一般0.1、0.2这样子
                                  subsample=self.dic_config['model_config']['xgboost_lr']['params']['subsample'],  # 随机采样训练样本 训练实例的子采样比，典型值的范围在0.5-0.9之间。
                                  colsample_bylevel=self.dic_config['model_config']['xgboost_lr']['params']['colsample_bylevel'],  # 生成树时进行的列采样 同subsample，一般在0.5-0.9
                                  objective=self.dic_config['model_config']['xgboost_lr']['params']['objective'],  # 二分类的问题,概率
                                  n_jobs=self.dic_config['model_config']['xgboost_lr']['params']['n_jobs'],  # 并行线程数
                                  seed=self.dic_config['model_config']['xgboost_lr']['params']['seed'],
                                  nthread=self.dic_config['model_config']['xgboost_lr']['params']['nthread'],  # 使用4个cpu进行计算
                                  )
        # model = xgb.XGBClassifier(learning_rate=0.1  # 学习率，过大收敛不了，小了收敛慢
        #                           , n_estimators=10
        #                           , max_depth=3  # 构建树的深度，越大越容易过拟合，可以用CV函数来进行调优
        #                           , scale_pos_weight=1
        #                           # 正样本的权重，在二分类任务中，当正负样本比例失衡时，设置正样本的权重，模型效果更好。例如，当正负样本比例为1:10时，scale_pos_weight=10。
        #                           , min_child_weight=1  # 叶子里面h的和，h就是二阶导不清楚的看看xgboost原理，该参数越小越容易过拟合
        #                           , gamma=0  # 树的叶子节点上作进一步分区所需的最小损失减少,越大越保守，一般0.1、0.2这样子
        #                           , subsample=1  # 随机采样训练样本 训练实例的子采样比，典型值的范围在0.5-0.9之间。
        #                           , colsample_bylevel=1  # 生成树时进行的列采样 同subsample，一般在0.5-0.9
        #                           , objective='binary:logistic'  # 二分类的问题,概率
        #                           , n_jobs=4  # 并行线程数
        #                           , seed=100
        #                           , nthread=4  # 使用4个cpu进行计算
        #                           )
        model.fit(x_train, y_train, eval_metric='auc', eval_set=eval_set, early_stopping_rounds=10)
        # model.fit(x_train, y_train)
        return model
    '''

    def train_no_auc(self, x_train, y_train):
        # 使用pipeline 方法
        pipeline = PMMLPipeline([("xgb", self.model)])
        # pipeline.fit(x_train, y_train)
        # sklearn2pmml(pipeline, "./data/xgboost.pmml", with_repr=True)
        self.model.fit(x_train, y_train, verbose=True)
        return self.model, pipeline  # 试下使用pipeline

    def train_with_auc(self, x_train, y_train, eval_set):
        print("start fit pipeline")
        # pipeline = Pipeline([
        # pipeline = PMMLPipeline([
        #     ('xgb', self.model)
        # ])

        # 下面xgb要和定义Pipeline时的key一样,先暂停一下
        # pipeline.fit(x_train, y_train,
        #              xgb__eval_metric='auc',
        #              xgb__early_stopping_rounds=self.dic_config['model_config']['xgboost_lr']['xgb_fit_params']['early_stopping_rounds'],
        #              xgb__eval_set=eval_set,
        #              xgb__verbose=True
        #              )

        # xgboost_to_pmml(pipeline, features, target, "xgb-iris.pmml")
        print("end fit pipeline")
        # pipeline = PMMLPipeline([("classifier", self.model)])
        # pipeline.fit(xtrain_top37vars, y_train,classifer__eval_set=[xgtrain_37vars, xgtest_37vars],classifer__eval_metric='auc')
        # pipeline.fit(x_train, y_train,
        #              classifer_eval_set=eval_set,
        #              classifer_eval_metric='auc'
                     # classifer_early_stopping_rounds=self.dic_config['model_config']['xgboost_lr']['xgb_fit_params']['early_stopping_rounds']
                     # )
        # sklearn2pmml(pipeline, "./data/xgboost.pmml", with_repr=True)

        self.model.fit(x_train,
                       y_train,
                       eval_metric='auc',
                       eval_set=eval_set,
                       early_stopping_rounds=self.dic_config['model_config']['xgboost_lr']['xgb_fit_params'][
                           'early_stopping_rounds'],
                       verbose=True
                       )

        # plot feature importance
        plot_importance(self.model)
        # pyplot.show()
        pyplot.savefig(self.dic_config['feature_importance_path'], dpi=1000)

        print("copy....")
        copy_model = self.model._Booster.copy()

        print(copy_model)

        # PMML模型文件导出
        pipeline = PMMLPipeline([
            ('xgb', self.model)
        ])

        pipeline.fit(x_train, y_train,
                     xgb__eval_metric='auc',
                     xgb__early_stopping_rounds=self.dic_config['model_config']['xgboost_lr']['xgb_fit_params'][
                         'early_stopping_rounds'],
                     xgb__eval_set=eval_set,
                     xgb__verbose=True
                     )

        sklearn2pmml(pipeline, self.dic_config['xgb_pmml_model_path'], with_repr=True)

        return self.model, pipeline

    def predict_proba(self, trained_model, x_test):
        probas = trained_model.predict_proba(x_test)
        # print(probas)
        # print(f'========')
        # # 测试copy
        # booster = xgb.Booster.copy(trained_model.get_booster())
        # ps = booster.predict(x_test)
        # print(ps)
        #
        # print("=========")
        # print(probas[:, 1])
        return probas

    def predict(self, trained_model, x_test):
        res = trained_model.predict(x_test)
        return res


'''
    def train_xgb_lr(self, xgb_model, x_train, y_train, x_test):
        """
        model: train_xgb 方法的返回
        """
        ##apply函数返回的是叶子索引
        x_train_leaves = xgb_model.apply(x_train).astype(np.int32)
        x_test_leaves = xgb_model.apply(x_test).astype(np.int32)
        # print(" = " * 10)
        # print(type(x_train_leaves))  # <class 'numpy.ndarray'>
        # print(x_train_leaves.shape)  # (559999, 10)
        # print(x_train_leaves)
        # print(" = " * 10)

        # 使用numpy的concatenate来拼接数组，并生成全局的onehot，单一使用train的可能会漏掉编码，test验证的时候出问题
        x_leaves = np.concatenate((x_train_leaves, x_test_leaves), axis=0)  # axis=0二维纵向拼接,union

        # print(f'Transform xgb leaves shape: {x_leaves.shape}')  # (859999, 10)

        xgb_onehotcoder = OneHotEncoder()
        xgb_onehotcoder.fit(x_leaves)

        self.x_train_lr = xgb_onehotcoder.transform(x_train_leaves).toarray()  # 转成one-hot编码
        x_test_lr = xgb_onehotcoder.transform(x_test_leaves).toarray()  # 转成one-hot编码

        # print(f'Transform xgb x_train_lr shape: {x_train_lr.shape}')  # (559999, 0)
        # print(f'Transform xgb x_test_lr shape: {x_test_lr.shape}')  # (300000, 80)

        lr_model = LogisticRegression()
        lr_model.fit(self.x_train_lr, y_train)

        return lr_model




    def train_xgb_lr2(self,x_train,y_train):

        ## hstack 进行one特征与原始特征的拼接
        x_train_lr2 = np.hstack((self.x_train_lr, x_train.values))  # :在水平方向上平铺,横向
        # print(f'Transform xgb x_train_lr2 shape: {x_train_lr2.shape}')  # (559999, 101)

        # !!!!
        # x_test_lr2 = np.hstack((x_test_lr, x_test.values))

        # print(f'Transform xgb x_test_lr2 shape: {x_test_lr2.shape}')  # (300000, 101)
        lr_model2 = LogisticRegression()
        lr_model2.fit(x_train_lr2, y_train)
        return lr_model2

    def predict(self, model, x_test):
        probas = model.predict_proba(x_test)
        return probas
'''
