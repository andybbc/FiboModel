import pickle

from sklearn.preprocessing import OneHotEncoder

from model.base import Base
from model.logistic_regression_rtb import LogisticRegressionRTBModel
from model.xgboost_rtb import XgboostRTBModel
import pandas as pd
import numpy as np
import joblib

from sklearn2pmml import sklearn2pmml, PMMLPipeline

from nyoka import xgboost_to_pmml

class Xgboost_lr_rtb(Base):

    def __init__(self, dic_config):
        super().__init__(dic_config)

        self.dic_config = dic_config
        self.logger = dic_config['logger']

        self.dev: bool = dic_config['dev']  # 需不需要拆分看效果,生产环境不需要拆分
        self.use_model_type = dic_config['use_model_type']  # 使用的模型类型 xgbgoot, xgboost_lr

        self.encode_file_path = dic_config['encode_file_path']  # 可以用于模型的文件,label后的文件
        self.out_one_hot_encoder_path = dic_config.get('out_one_hot_encoder_path')  # one_hot_encode的中间文件路径

        self.train_file_path = dic_config.get('train_file_path')
        self.vali_file_path = dic_config.get('vali_file_path')
        self.test_file_path = dic_config.get('test_file_path')
        # 保存的model的路径
        self.xgb_model_path = dic_config.get('xgb_model_path')
        self.xgb_pmml_model_path = dic_config.get('xgb_pmml_model_path')
        self.lr_model_path = dic_config.get('lr_model_path')
        self.lr_pmml_model_path = dic_config.get('lr_pmml_model_path')
        # 指明dataFrame的数据类型
        # self.dtype={k,v for k,v in }

        self.feature_importance_path = dic_config.get('feature_importance_path')

    def load_data(self):
        # 需要指明数据类型
        # dic_config['need_label_encode_cols_num']
        # 判断需不需要拆分,上生产环境不需要拆分
        if self.dev:
            # 拆分,做auc,观察效果
            df_train = pd.read_csv(self.train_file_path, header=None, sep=self.dic_config['file_separator'], encoding=u'utf-8')
            df_vali = pd.read_csv(self.vali_file_path, header=None, sep=self.dic_config['file_separator'], encoding=u'utf-8')
            df_test = pd.read_csv(self.test_file_path, header=None, sep=self.dic_config['file_separator'], encoding=u'utf-8')

            self.cols = list(map(str, df_train.columns.tolist()))  # 所有的
            print("=" * 10)
            print(self.cols)
            ##数据准备
            self.y_train = df_train[0]
            self.x_train = df_train.iloc[:, 1:]  # 从第二列开始往又所有(包括第二列)

            self.y_vali = df_vali[0]
            self.x_vali = df_vali.iloc[:, 1:]

            self.y_test = df_test[0]
            self.x_test = df_test.iloc[:, 1:]
        else:
            # 不需要拆分,直接按照label_encode后的文件训练
            df_train = pd.read_csv(self.encode_file_path, header=None, sep=self.dic_config['file_separator'], encoding=u'utf-8')
            ##数据准备,只有一个文件
            self.y_train = df_train[0]
            self.x_train = df_train.iloc[:, 1:]  # 从第二个开始往又所有

    def dump_model(self, model, path):
        joblib.dump(model, path)
        print("开始自定义生成模型文件")
        # model._Booster.save_model(path+"_2")


    # one_hot_encode训练,保存模型
    def one_hot_encoder_train(self):
        """
        生成one host encoder的时候顺便把对象保存下来
        """
        xgb_onehotcoder = OneHotEncoder()
        xgb_onehotcoder.fit(self.x_leaves)
        # 把label_dict导入到文件
        with open(self.out_one_hot_encoder_path, 'wb') as f:
            pickle.dump(xgb_onehotcoder, f)
        return xgb_onehotcoder


    def train(self):
        xgb_lr_model = XgboostRTBModel(self.dic_config)
        # 判断需不需要拆分,上生产环境不需要拆分
        if self.dev:
        # 拆分,做auc,观察效果
            eval_set = [(self.x_vali, self.y_vali)]
            xgb_model_res, pipeline = xgb_lr_model.train_with_auc(self.x_train, self.y_train, eval_set)
            # self.dump_model(xgb_model_res, self.xgb_model_path)
            joblib.dump(xgb_model_res, self.xgb_model_path)
            xgb_model_res._Booster.save_model(self.xgb_model_path + "_2")

            features = list(map(str, range(1, self.x_train.shape[1] + 1)))  # 特征名称,用1-xx 代替
            target = 'label'

            # xgboost_to_pmml(pipeline, self.cols[1:], self.cols[0], self.xgb_model_path+"_pmml")  # 下标越界????
            # sklearn转换为pmml,先暂停一下
            # sklearn2pmml(pipeline, self.xgb_model_path + "_3_pipeline", with_repr=True)

            # xgboost后面使用LR
            if self.use_model_type == 'xgboost_lr':
                print("==== LogisticRegression train ====")
                # 我们来拿到xgb的叶子节点的特征
                x_train_leaves = xgb_model_res.apply(self.x_train).astype(np.int32)
                x_test_leaves = xgb_model_res.apply(self.x_test).astype(np.int32)
                self.x_leaves = np.concatenate((x_train_leaves, x_test_leaves), axis=0)  # axis=0二维纵向拼接,union

                xgb_onehotcoder = self.one_hot_encoder_train()  # 训练
                x_train_lr = xgb_onehotcoder.transform(x_train_leaves).toarray()  # 转成one-hot编码
                lr_ctr_model = LogisticRegressionRTBModel(self.dic_config)
                lr_model = lr_ctr_model.train(x_train_lr, self.y_train)
                # self.dump_model(lr_model, self.lr_model_path)
                joblib.dump(lr_model, self.lr_model_path)  # 生成二进制文件
                # PMML模型文件导出
                pipeline = PMMLPipeline([
                    ('classifier', lr_model)
                ])
                sklearn2pmml(pipeline, self.lr_pmml_model_path, with_repr=True)
                print("==== end LogisticRegression train ====")

        else:  # 不需要拆分的
            xgb_model_res, pipeline = xgb_lr_model.train_no_auc(self.x_train, self.y_train)
            self.dump_model(xgb_model_res, self.xgb_model_path)
            # sklearn转换为pmml
            sklearn2pmml(pipeline, self.xgb_model_path+"_3_pipeline", with_repr=True)

            # from nyoka import xgboost_to_pmml转换
            # 参考:https://www.codeleading.com/article/16804233848/
            # features = list(map(str, range(1, self.x_train.shape[1] + 1)))
            # print(f"features == {features}")
            # xgboost_to_pmml(xgb_model_res, features, "0", self.xgb_model_path+"_4_pipeline")

            # xgboost后面使用LR
            if self.use_model_type == 'xgboost_lr':
                print("开始lr训练")
                # 我们来拿到xgb的叶子节点的特征
                x_train_leaves = xgb_model_res.apply(self.x_train).astype(np.int32)
                self.x_leaves = x_train_leaves
                xgb_onehotcoder = self.one_hot_encoder_train()  # 训练
                x_train_lr = xgb_onehotcoder.transform(x_train_leaves).toarray()  # 转成one-hot编码
                lr_ctr_model = LogisticRegressionRTBModel(self.dic_config)
                lr_model = lr_ctr_model.train(x_train_lr, self.y_train)
                self.dump_model(lr_model, self.lr_model_path)

