import sys

sys.path.append("..")
import numpy as np
import xgboost as xgb
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.model_selection import KFold
from model.base import Base
import pandas as pd
from conf.reco._xgboost import params, train_params, k_fold_params,text_params


class XGBoost(Base):
    """
    采用Xgboost算法进行分类，要求输入训练数据路径，测试数据路径，数据总类数
    训练数据和测试数据要求均为csv格式，
    第一列为类别（number），
    第二列为文本
    """

    # def __init__(self, train_path, test_path, num_round, log_file):
    def __init__(self, dic_config: dict):
        Base.__init__(self, dic_config)
        self.dic_config = dic_config
        self.model_path = dic_config['model_path']  # 模型文件输出路径

    def train(self, X_train, X_test, y_train, y_test):
        """
        模型训练
        :param X_train: 
        :param X_test: 
        :param y_train: 
        :param y_test: 
        :return: 
        """
        xgb_train = xgb.DMatrix(X_train, label=y_train)
        xgb_test = xgb.DMatrix(X_test, label=y_test)
        watchlist = [(xgb_train, 'train'), (xgb_test, 'test')]
        # print(f'====={xgb_test.feature_types}')
        # print(f'============={self.num_round}')

        bst = xgb.train(params, xgb_train, num_boost_round=train_params['num_round'], evals=watchlist,
                        verbose_eval=train_params['verbose_eval']
                        , early_stopping_rounds=train_params['early_stopping_rounds'])

        # 模型预测
        pred = bst.predict(xgb_test)

        # 模型评估
        error_rate = np.sum(pred != y_test) / y_test.shape[0]
        self.logger.info('测试集错误率(softmax):{}'.format(error_rate))
        accuray = 1 - error_rate
        self.logger.info('测试集准确率：%.4f' % accuray)

        return bst

    def predict(self, df , bst):
        """
        模型预测
        :param x_test:
        :return:
        """

        xgb_test = xgb.DMatrix(df)
        pred = bst.predict(xgb_test)
        return pred
        # print(pred.shape)
        # print(type(pred.shape))
        # df = pd.DataFrame(pred)
        # df.to_csv(out_path, header=False, index=False)

    # def predict_batch(self, x_test):
    #     """
    #     模型预测
    #     :param x_test:
    #     :return:
    #     """
    #     # 模型加载
    #     bst = xgb.Booster()
    #     bst.load_model(self.model_path)
    #
    #     xgb_test = xgb.DMatrix(x_test)
    #     # 模型加载
    #     bst = xgb.Booster()
    #     bst.load_model(self.model_path)
    #     pred = bst.predict(xgb_test)
    #     return pred

    # K折交叉验证,调试参数用
    def k_fold_test(self, data, train_x, train_y):  #
        # test_pred_prob = np.zeros(test.shape[0])

        folds = KFold(n_splits=k_fold_params['n_splits'], shuffle=k_fold_params['shuffle'],
                      random_state=k_fold_params['random_state'])

        feature_importance_df = pd.DataFrame()
        for fold_, (trn_idx, val_idx) in enumerate(folds.split(data)):
            self.logger.info("=== fold {} ===".format(fold_ + 1))
            trn_data = xgb.DMatrix(train_x.iloc[trn_idx], label=train_y[trn_idx])
            val_data = xgb.DMatrix(train_x.iloc[val_idx], label=train_y[val_idx])
            watchlist = [(trn_data, 'train'), (val_data, 'valid')]
            bst = xgb.train(params, trn_data, train_params['num_round'], watchlist,
                            verbose_eval=train_params['verbose_eval'],
                            early_stopping_rounds=train_params['early_stopping_rounds'])

            pred_df = bst.predict(xgb.DMatrix(train_x.iloc[val_idx]), ntree_limit=bst.best_ntree_limit)

            fold_importance_df = pd.DataFrame()
            fold_importance_df["Feature"] = bst.get_fscore().keys()
            fold_importance_df["importance"] = bst.get_fscore().values()
            fold_importance_df["fold"] = fold_ + 1
            feature_importance_df = pd.concat([feature_importance_df, fold_importance_df], axis=0)  # 跨行,行连接,类似union

            # ressss = bst.predict(xgb.DMatrix(test), ntree_limit=bst.best_ntree_limit) / folds.n_splits
            # print("aaa=================================================")
            # print(f"resss.shape{ressss.shape}")
            # print(f"resss.shape{ressss}")
            # print("aaa=================================================")
            # test_pred_prob += ressss
            # 模型预测

            # 模型评估
            error_rate = np.sum(pred_df != train_y[val_idx]) / train_y[val_idx].shape[0]
            self.logger.info('测试集错误率(softmax):{}'.format(error_rate))
            accuray = 1 - error_rate
            self.logger.info('测试集准确率：%.4f' % accuray)

    #####################下面是文本分类##########################

    # 文本分类训练
    def text_train(self,train_content,train_option):
        vectorizer = CountVectorizer()
        tfidftransformer = TfidfTransformer()
        tfidf = tfidftransformer.fit_transform(vectorizer.fit_transform(train_content))
        # self.logger.info(type(tfidf))
        weight = tfidf.toarray()
        # self.logger.info(tfidf.shape)

        dtrain = xgb.DMatrix(weight, label=train_option)
        # param = {'max_depth': 6, 'eta': 0.5, 'eval_metric': 'merror', 'silent': 1, 'objective': 'multi:softmax',
        #          'num_class': self.class_number}  # 参数
        #params, xgb_train, num_boost_round=train_params['num_round'], evals=watchlist,
              #          verbose_eval=train_params['verbose_eval']
              #          , early_stopping_rounds=train_params['early_stopping_rounds'])

        evallist = [(dtrain, 'train')]  # 这步可以不要，用于测试效果
        # num_round = 50  # 循环次数
        self.logger.info('开始训练模型')
        bst = xgb.train(text_params, dtrain, train_params['num_round'], evallist)
        self.logger.info('模型训练完成')
        return bst

    # 文本预估要先执行这个!!!!!!!!!!!!!!!!!!!!!!
    def fit_transform(self, train_content):
        self.vectorizer = CountVectorizer()
        self.tfidftransformer = TfidfTransformer()
        self.tfidftransformer.fit_transform(self.vectorizer.fit_transform(train_content))


    def text_predict(self,test_content, bst):
        # vectorizer = CountVectorizer()
        # tfidftransformer = TfidfTransformer()
        # print("============" * 2)
        # print(type(test_content))  # <class 'list'>
        # print(test_content[0])
        # print("len(test_content)")
        # print(len(test_content))
        # print("++++++++++++" * 2)
        # tfidftransformer.fit_transform(vectorizer.fit_transform(train_content))

        test_tfidf = self.tfidftransformer.transform(self.vectorizer.transform(test_content))
        test_weight = test_tfidf.toarray()
        # self.logger.info(test_weight.shape)
        dtest = xgb.DMatrix(test_weight)
        preds = bst.predict(dtest)
        return preds

