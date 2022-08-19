import sys

from preprocess.segment_words import segment_words

sys.path.append("..")
from .base import Base
import pandas as pd
from model._xgboost import XGBoost as xgb_model
import xgboost as xgb


class XGBoost(Base):

    def __init__(self, dic_config):
        super().__init__(dic_config)
        self.dic_config = dic_config
        self.model_path = dic_config['model_path']
        self.test_path = dic_config['test_path']
        self.out_path = dic_config['out_path']

        # 初始化Predict对象时就加载xgboost_model
        xgboost_model = xgb_model(self.dic_config)
        self.xgboost_model = xgboost_model
        self.s_w = segment_words(self.dic_config)

    def load_model(self):
        # 模型加载
        bst = xgb.Booster()
        bst.load_model(self.model_path)
        return bst

    def load_data(self):
        data = pd.read_csv(self.test_path, header=None, sep=',')
        return data

    # def predict(self):
    #     # data2['label'] = -1
    #     xgboost_model = xgb_model(self.dic_config)
    #
    #     # xgb_test = xgb.DMatrix(X_test,)
    #     # 模型加载
    #     # bst = xgb.Booster()
    #     # bst.load_model(self.model_path)
    #
    #     # clf.predict(xgb.DMatrix(test), ntree_limit=clf.best_ntree_limit)
    #
    #     xgboost_model.predict(data, self.model_path, self.out_path)
    #     # clf.predict(xgb.DMatrix(test), ntree_limit=clf.best_ntree_limit)
    #     # xgb_test = xgb.DMatrix(X_test, label=y_test)

    # 预测一个值
    def predict_one(self, test_srt, bst):
        arr = test_srt.split(",")
        df = pd.DataFrame(arr, dtype=float).T
        # xgboost_model = xgb_model(self.dic_config)

        pred = self.xgboost_model.predict(df, bst)
        return pred
        # print(pred)

    def predict_batch(self):
        # data2['label'] = -1
        # bst = xgb.Booster()
        # xgb_test = xgb.DMatrix(X_test,)

        df = pd.read_csv(self.dic_config['test_path'])
        # clf.predict(xgb.DMatrix(test), ntree_limit=clf.best_ntree_limit)
        # 模型加载
        bst = self.load_model()
        pred_res = self.xgboost_model.predict(df, bst)
        df = pd.DataFrame(pred_res)
        df.to_csv(self.out_path, header=False, index=False)

    ## !!! 预估要先跑这个
    def text_load_and_fit_train_data(self):
        train_content, train_option = self.s_w.text_load_train_data()
        self.xgboost_model.fit_transform(train_content)


    def text_predict_one(self, string, bst):

        test_content = self.s_w.text_load_test_data(string)
        preds = self.xgboost_model.text_predict(test_content, bst)
        return preds

    def text_predict_batch(self):
        bst = self.load_model()
        train_content, train_option = self.s_w.text_load_train_data()
        test_content = self.s_w.text_load_test_data()  # <class 'list'>

        self.xgboost_model.fit_transform(train_content)

        # print(f"type testContent:{type(test_content)}")  # <class 'list'>
        pred_res = self.xgboost_model.text_predict(test_content, bst)
        # print("type(pred_res)")
        # print(type(pred_res))
        # print("type(pred_res)")
        # df = pd.DataFrame(pred_res)
        # df.to_csv(self.out_path, header=False, index=False)
        self.write_file(self.out_path, pred_res)

    def write_file(self, out_path,pred_res):
        with open(out_path, 'w') as f:
            for i, pre in enumerate(pred_res):
                # f.write(str(i + 1))
                # f.write(',')
                f.write(str(int(pre) + 1))
                f.write('\n')
        self.logger.info('预测完成，数据写入%s文件' % out_path)

