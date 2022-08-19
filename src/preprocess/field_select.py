import pandas as pd
from sklearn import preprocessing
import joblib

import warnings
import numpy as np
import json

from model.base import Base
import matplotlib.pyplot as plt
from sklearn import manifold

warnings.filterwarnings("ignore")
# 序列化用
import pickle

import toad

from datetime import datetime

#  文件预处理

class FieldSelect(Base):
    """
    文件输入第一行为表头,
    包含 lable_encode文件和label_encode映射
    """

    def __init__(self, dic_config):
        super().__init__(dic_config)

        self.dic_config = dic_config
        self.logger = dic_config['logger']

        self.file_separator = dic_config["file_separator"]

        self.origin_path = dic_config.get('origin_path')  # 原始输入文件,包含点击字段
        self.split_cols_file_path = dic_config.get('split_cols_file_path')  # 生成的自定义拆分原始文件的路径
        self.encode_file_path = dic_config.get('encode_file_path')  # 可以用于模型的文件,label后的文件
        self.out_label_path = dic_config.get('out_label_path')  # 记住映射
        self.out_label_detail_path = dic_config.get('out_label_detail_path')
        self.label_dict = {}  # 存放label映射

        self.train_file_path = dic_config.get('train_file_path')
        self.vali_file_path = dic_config.get('vali_file_path')
        self.test_file_path = dic_config.get('test_file_path')

        self.need_label_encode_cols_num = dic_config.get('need_label_encode_cols_num')
        self.select_cols = dic_config.get('select_cols')  # 按列拆分文件

        #  类型:如果是训练文件,第一列包含label字段,如果是预测文件,则不包含第一列label字段
        self.split_file_type = dic_config["split_file_type"]
        # 是否需要归一化
        # self.if_minmaxscaler: bool = True if dic_config.get('if_minmaxscaler') else False
        # self.if_minmaxscaler: bool = dic_config.get('if_minmaxscaler')
        self.dense_feature_type = dic_config.get('dense_feature_type')  # 数值型的归一化处理方式 # minmaxscaler / log /none

        self.mms_save_file = dic_config.get('mms_save_file')  # 数值字段归一化的fit后的保存文件路径
        self.tne_file_path = dic_config.get('tne_file_path')  # tne散点图文件路径

    def split_file_cols(self):
        """
        第一步:先拆分字段,选择需要的字段后然后再label_encode/数值转换
        将原始文件按照 select_cols 拆分,第一列为label列
        :return:
        """
        print(f"========== select_cols : {self.select_cols} ==========")
        if self.split_file_type == "train":
            # 如果是训练数据,则包含第一列label
            # if 0 in self.select_cols:
            #     df = pd.read_csv(self.origin_path, header=None, sep=self.file_separator, encoding=u'utf-8', dtype=str)
            #     df_after = df[self.select_cols]
            #     df_after.to_csv(self.split_cols_file_path, header=False, index=False,
            #                     sep=self.file_separator,
            #                     encoding=u'utf-8')
            # else:
            #     raise Exception("select_cols需要包含label列")

            df = pd.read_csv(self.origin_path, header=None, sep=self.file_separator, encoding=u'utf-8', dtype=str)
            df_after = df[self.select_cols]
            df_after.to_csv(self.split_cols_file_path, header=False, index=False,
                            sep=self.file_separator,
                            encoding=u'utf-8')

        elif self.split_file_type == "predict":
            # 是预测文件,不包含第一列label字段
            if 0 in self.select_cols:
                df = pd.read_csv(self.origin_path, header=None, sep=self.file_separator,
                                 encoding=u'utf-8', dtype=str)
                # temp_cols = self.select_cols[1:]
                # df_after = df[[x - 1 for x in temp_cols]]
                df_after = df[self.select_cols]
                df_after.to_csv(self.split_cols_file_path, header=False, index=False,
                                sep=self.file_separator, encoding=u'utf-8')
            else:
                raise Exception("select_cols需要包含label列,预测文件比训练文件少了第一列,但是扔旧使用训练的选择列")
        else:
            raise Exception("未知的split_file_type [ train ] or [ predict ]")

    # 需要的列转换
    def label_encode_data(self):
        '''
        如果有字符串字段则做label_encode
        根据参数判断是否需要将剩余数值字段做minmaxscaler,做简单的归一化
        ## 只针对训练文件(第一列为label)
        :return:
        '''
        if self.split_file_type == "train":
            # 训练文件转换
            self._label_encode_data_train()
        elif self.split_file_type == "predict":
            # 预估数据处理
            self._label_encode_data_predict()
        else:
            raise Exception("未知的split_file_type [ train ] or [ predict ]")

    def split_data(self):
        # header= None 表头不是第一行
        df = pd.read_csv(self.encode_file_path, header=None, sep=self.file_separator, encoding=u'utf-8')
        df_1 = df[df[0] == 1]  # label字段==1的筛选
        df_0 = df[df[0] == 0]
        self.df_1 = df_1
        self.df_0 = df_0

        df_1_test = df_1.sample(frac=0.3, random_state=100)  # test的数据
        df_0_test = df_0.sample(frac=0.3, random_state=100)  # test数据

        df_1_other = df_1[~df_1.index.isin(df_1_test.index)]  # 剩下的
        df_0_other = df_0[~df_0.index.isin(df_0_test.index)]

        df_1_vali = df_1_other.sample(frac=0.2, random_state=100)  # 取到vali的数据
        df_0_vali = df_0_other.sample(frac=0.2, random_state=100)  # 取到vali的数据

        df_1_train = df_1_other[~df_1_other.index.isin(df_1_vali.index)]  # 取到剩下的训练的数据
        df_0_train = df_0_other[~df_0_other.index.isin(df_0_vali.index)]  # 取到剩下的训练的数据

        # 合并1/0
        df_train = pd.concat([df_1_train, df_0_train], ignore_index=True)
        df_vali = pd.concat([df_1_vali, df_0_vali], ignore_index=True)
        df_test = pd.concat([df_1_test, df_0_test], ignore_index=True)

        df_train.to_csv(self.train_file_path, header=False, sep=self.file_separator, encoding=u'utf-8',
                        index=False)
        df_vali.to_csv(self.vali_file_path, header=False, sep=self.file_separator, encoding=u'utf-8',
                       index=False)
        df_test.to_csv(self.test_file_path, header=False, sep=self.file_separator, encoding=u'utf-8',
                       index=False)

    # 显示正负样本分布
    def show_tne(self):
        print("show_tne==begin")
        tsne = manifold.TSNE(n_components=2, init='pca', random_state=0)
        Y_0 = tsne.fit_transform(self.df_0)  # 转换后的输出
        Y_1 = tsne.fit_transform(self.df_1)
        print(Y_0)
        print(Y_1)
        plt.title("tsne sample")
        #显示负样本散点图
        plt.scatter(Y_0[:, 0], Y_0[:, 1], c='b', s=0.1)
        #显示正样本散点图
        plt.scatter(Y_1[:, 0], Y_1[:, 1], c='r', s=0.1)
        # plt.show()
        plt.savefig(self.tne_file_path, dpi=1000)
        print("show_tne==END")

    # # 单个列处理
    # def _one_label_encode_train(self, field_index, df):
    #     dic = []
    #     df_field = df.iloc[:, field_index]  # 提取第几列
    #     list_field = df_field.tolist()
    #
    #     # 构建field字典
    #     for i in list_field:
    #         if i not in dic:
    #             dic.append(i)
    #
    #     label_field = preprocessing.LabelEncoder()
    #     label_field.fit(dic)
    #
    #     # 保存label
    #     self.label_dict[field_index] = label_field
    #     df_field_enconde_tmp = None
    #     try:
    #         df_field_enconde_tmp = label_field.transform(df_field)
    #     except:
    #         print(f'第{field_index}列label_encode异常')
    #         print(field_index)
    #         print(df)
    #
    #     df_field_enconde = pd.DataFrame(df_field_enconde_tmp)
    #     return df_field_enconde

    # 单个列处理
    def _one_label_encode_train(self, field_index, df):
        dic = []

        # real_df_field = df.iloc[:, field_index]  # 提取第几列

        # if field_index == 4:
        #     df2 = pd.read_csv("/data/algorithm/python-ctr-model/data/xgboost/feature/tmp/behavior_summary_day_20210825_producer.csv", header=None, sep='#', encoding=u'utf-8')
        #     df_field = df2.iloc[:, 0]
        #     # 把数据库和样本数据合并
        #     df_field = pd.concat([df_field, real_df_field], axis=0)
        # elif field_index == 5:
        #     df2 = pd.read_csv("/data/algorithm/python-ctr-model/data/xgboost/feature/tmp/behavior_summary_day_20210825_model.csv", header=None, sep='#', encoding=u'utf-8')
        #     df_field = df2.iloc[:, 0]
        #     df_field = pd.concat([df_field, real_df_field], axis=0)
        # elif field_index == 6:
        #     df2 = pd.read_csv("/data/algorithm/python-ctr-model/data/xgboost/feature/tmp/behavior_summary_day_20210825_osv.csv", header=None, sep='#', encoding=u'utf-8')
        #     df_field = df2.iloc[:, 0]
        #     df_field = pd.concat([df_field, real_df_field], axis=0)
        # elif field_index == 7:
        #     df2 = pd.read_csv("/data/algorithm/python-ctr-model/data/xgboost/feature/tmp/behavior_summary_day_20210825_brand.csv", header=None, sep='#', encoding=u'utf-8')
        #     df_field = df2.iloc[:, 0]
        #     df_field = pd.concat([df_field, real_df_field], axis=0)
        # elif field_index == 13:
        #     df2 = pd.read_csv("/data/algorithm/python-ctr-model/data/xgboost/feature/tmp/behavior_summary_day_20210825_pkg_name.csv", header=None, sep='#', encoding=u'utf-8')
        #     df_field = df2.iloc[:, 0]
        #     df_field = pd.concat([df_field, real_df_field], axis=0)
        # else:
        #     df_field = df.iloc[:, field_index]  # 提取第几列

        df_field = df.iloc[:, field_index]  # 提取第几列
        list_field = df_field.tolist()

        # 构建field字典
        for i in list_field:
            if i not in dic:
                dic.append(i)

        label_field = preprocessing.LabelEncoder()
        label_field.fit(dic)

        # 保存label
        self.label_dict[field_index] = label_field
        df_field_enconde_tmp = None
        try:
            df_field_enconde_tmp = label_field.transform(df_field)
            # df_field_enconde_tmp = label_field.transform(real_df_field)
        except:
            print(f'第{field_index}列label_encode异常')
            print(field_index)
            print(df)

        df_field_enconde = pd.DataFrame(df_field_enconde_tmp)
        return df_field_enconde

    # def _label_encode_data_train(self):
    #     # 需要转换类型,防止label_encode的字段变成int
    #     sparse_feature_dtype = {i: str for i in
    #                             range(len(self.select_cols) - self.need_label_encode_cols_num,
    #                                   len(self.select_cols))}
    #
    #     df = pd.read_csv(self.split_cols_file_path, header=None, sep=self.dic_config['file_separator'],
    #                      encoding=u'utf-8', dtype=sparse_feature_dtype)
    #     # df.dropna(axis=0, how='any')  # 删除有nan的行,上游生成文件的时候保证就行了,这边不需要做处理
    #
    #     cols_num = df.shape[1]
    #     # df.dropna(axis=0, how='any')  # 删除有nan的行
    #     # 前面数值部分填充0
    #     df[[i for i in range(0, cols_num - self.need_label_encode_cols_num + 1)]] = \
    #         df[[i for i in range(0, cols_num - self.need_label_encode_cols_num + 1)]].fillna(0, )
    #
    #     # 后面不是数值的部分填充'-1'
    #     if self.need_label_encode_cols_num:
    #         df[[i for i in range(cols_num - self.need_label_encode_cols_num, cols_num)]] = \
    #             df[[i for i in range(cols_num - self.need_label_encode_cols_num, cols_num)]].fillna('-1')
    #
    #     if self.need_label_encode_cols_num:  # 如果需要label_encode,如果不为0
    #         # 转换需要转换的字段的list
    #         label_df_list = [*map(lambda index: self._one_label_encode_train(index, df),
    #                               [x for x in range((0 - self.need_label_encode_cols_num), 0)])]  # -3, -2, -1
    #
    #         if self.need_label_encode_cols_num == len(self.select_cols) - 1:  # 出了label列,都要label_encode处理
    #             pd_stg_input = pd.concat([df[[0]], *label_df_list], axis=1)  # 传入可变参数
    #         else:
    #             # 针对原本是数值型的字段,判断是否需要归一化处理
    #             if self.dense_feature_type == "minmaxscaler":
    #                 df_dense = df.iloc[:, 1: -self.need_label_encode_cols_num]
    #                 mms = preprocessing.MinMaxScaler(feature_range=(0, 1))
    #                 mms.fit(df_dense)  # 先适配一下,然后保存下来
    #                 # 保存成文件,待预测使用
    #                 joblib.dump(mms, self.mms_save_file)
    #                 df_mms = mms.transform(df_dense)  # 归一化后的dataframe
    #                 pd_stg_input = pd.concat([df[[0]], pd.DataFrame(df_mms), *label_df_list], axis=1)  # 传入可变参数
    #             elif self.dense_feature_type == "log":
    #                 df_dense = df.iloc[:, 1: -self.need_label_encode_cols_num]
    #                 # 前面数值部分log处理
    #                 for i in range(1, cols_num - self.need_label_encode_cols_num):
    #                     df_dense[i] = df_dense[i].apply(lambda x: np.log(x + 1) if x > -1 else -1)
    #
    #                 pd_stg_input = pd.concat([df[[0]], df_dense, *label_df_list], axis=1)  # 传入可变参数
    #             else:  # none
    #                 # 数值部分不做处理(不管是训练文件还是预测文件)
    #                 pd_stg_input = pd.concat([df.iloc[:, : -self.need_label_encode_cols_num], *label_df_list], axis=1)
    #
    #         # 输出文件
    #         pd_stg_input.to_csv(self.encode_file_path, header=False, index=False,
    #                             sep=self.file_separator,
    #                             encoding=u'utf-8')
    #         self.pd_stg_input = pd_stg_input
    #         # 把label_dict导入到文件
    #         with open(self.out_label_path, 'wb') as f:
    #             pickle.dump(self.label_dict, f)
    #
    #         # 把映射关系输出
    #         label_detail_dict = {}
    #         for key, labelEncoder in self.label_dict.items():
    #             label_detail_dict[key] = dict(zip(labelEncoder.classes_.tolist(), range(0, len(labelEncoder.classes_))))
    #         with open(self.out_label_detail_path, 'w') as f:
    #             json.dump(label_detail_dict, f, indent=4)
    #
    #     else:  # 不需要label_encode,全部为数值型的字段
    #         # 针对原本是数值型的字段,判断是否需要归一化处理
    #         if self.dense_feature_type == "minmaxscaler":
    #             df_dense = df.iloc[:, 1:]
    #             mms = preprocessing.MinMaxScaler(feature_range=(0, 1))
    #             mms.fit(df_dense)  # 先适配一下,然后保存下来
    #             aa = mms.transform(df_dense)
    #             print(aa)
    #             # 保存成文件,待预测使用
    #             joblib.dump(mms, self.mms_save_file)
    #             df_mms = mms.transform(df_dense)  # 归一化后的dataframe
    #             pd_stg_input = pd.concat([df[[0]], pd.DataFrame(df_mms)],
    #                                      axis=1)  # 传入可变参数
    #
    #             pd_stg_input.to_csv(self.encode_file_path, header=False, index=False,
    #                                 sep=self.file_separator,
    #                                 encoding=u'utf-8')
    #
    #         elif self.dense_feature_type == "log":
    #             df_dense = df.iloc[:, 1:]
    #             # 前面数值部分log处理
    #             for i in range(1, cols_num):
    #                 df_dense[i] = df_dense[i].apply(lambda x: np.log(x + 1) if x > -1 else -1)
    #
    #             pd_stg_input = pd.concat([df[[0]], df_dense], axis=1)  # 传入可变参数
    #             pd_stg_input.to_csv(self.encode_file_path, header=False, index=False,
    #                                 sep=self.file_separator,
    #                                 encoding=u'utf-8')
    #
    #         else:
    #             # 直接原文件输出
    #             df.to_csv(self.encode_file_path, header=False, index=False, sep=self.file_separator,
    #                       encoding=u'utf-8')

    def _label_encode_data_train(self):
        # 需要转换类型,防止label_encode的字段变成int
        # sparse_feature_dtype = {i: str for i in
        #                         range(len(self.select_cols) - self.need_label_encode_cols_num,
        #                               len(self.select_cols))}

        sparse_feature_dtype = {i: str for i in
                                range(1, self.need_label_encode_cols_num + 1)}

        df = pd.read_csv(self.split_cols_file_path, header=None, sep=self.dic_config['file_separator'],
                         encoding=u'utf-8', dtype=sparse_feature_dtype)
        # df.dropna(axis=0, how='any')  # 删除有nan的行,上游生成文件的时候保证就行了,这边不需要做处理

        # 最后一列etl_date转换成周几
        df.iloc[:, -1] = df.iloc[:, -1].map(lambda x: datetime.strptime(x, '%Y-%m-%d').isoweekday())

        cols_num = df.shape[1]
        # df.dropna(axis=0, how='any')  # 删除有nan的行
        # 前面数值部分填充0
        # df[[i for i in range(0, cols_num - self.need_label_encode_cols_num + 1)]] = \
        #     df[[i for i in range(0, cols_num - self.need_label_encode_cols_num + 1)]].fillna(0, )
        # 前面需要编码的字段填充unknown
        df[[i for i in range(0, self.need_label_encode_cols_num + 1)]] = \
            df[[i for i in range(0, self.need_label_encode_cols_num + 1)]].fillna('unknown', )

        # # 后面不是数值的部分填充'-1'
        # if self.need_label_encode_cols_num:
        #     df[[i for i in range(cols_num - self.need_label_encode_cols_num, cols_num)]] = \
        #         df[[i for i in range(cols_num - self.need_label_encode_cols_num, cols_num)]].fillna('-1')
        # 后面不需要编码的字段填充-1
        if self.need_label_encode_cols_num:
            df[[i for i in range(self.need_label_encode_cols_num + 1, cols_num)]] = \
                df[[i for i in range(self.need_label_encode_cols_num + 1, cols_num)]].fillna(-1)

        if self.need_label_encode_cols_num:  # 如果需要label_encode,如果不为0
            # 转换需要转换的字段的list
            # label_df_list = [*map(lambda index: self._one_label_encode_train(index, df),
            #                       [x for x in range((0 - self.need_label_encode_cols_num), 0)])]  # -3, -2, -1

            label_df_list = [*map(lambda index: self._one_label_encode_train(index, df),
                                  [x for x in range(1, (self.need_label_encode_cols_num + 1))])]  # -3, -2, -1

            if self.need_label_encode_cols_num == len(self.select_cols) - 1:  # 出了label列,都要label_encode处理
                pd_stg_input = pd.concat([df[[0]], *label_df_list], axis=1)  # 传入可变参数
            else:
                # 针对原本是数值型的字段,判断是否需要归一化处理
                if self.dense_feature_type == "minmaxscaler":
                    df_dense = df.iloc[:, 1: -self.need_label_encode_cols_num]
                    mms = preprocessing.MinMaxScaler(feature_range=(0, 1))
                    mms.fit(df_dense)  # 先适配一下,然后保存下来
                    # 保存成文件,待预测使用
                    joblib.dump(mms, self.mms_save_file)
                    df_mms = mms.transform(df_dense)  # 归一化后的dataframe
                    pd_stg_input = pd.concat([df[[0]], pd.DataFrame(df_mms), *label_df_list], axis=1)  # 传入可变参数
                elif self.dense_feature_type == "log":
                    df_dense = df.iloc[:, 1: -self.need_label_encode_cols_num]
                    # 前面数值部分log处理
                    for i in range(1, cols_num - self.need_label_encode_cols_num):
                        df_dense[i] = df_dense[i].apply(lambda x: np.log(x + 1) if x > -1 else -1)

                    pd_stg_input = pd.concat([df[[0]], df_dense, *label_df_list], axis=1)  # 传入可变参数
                else:  # none
                    # 数值部分不做处理(不管是训练文件还是预测文件)
                    # pd_stg_input = pd.concat([df.iloc[:, : -self.need_label_encode_cols_num], *label_df_list], axis=1)
                    pd_stg_input = pd.concat([df.iloc[:, 0], *label_df_list, df.iloc[:, self.need_label_encode_cols_num + 1:]], axis=1)

            # 输出文件
            pd_stg_input.to_csv(self.encode_file_path, header=False, index=False,
                                sep=self.file_separator,
                                encoding=u'utf-8')
            self.pd_stg_input = pd_stg_input
            # 把label_dict导入到文件
            with open(self.out_label_path, 'wb') as f:
                pickle.dump(self.label_dict, f)

            # 把映射关系输出
            label_detail_dict = {}
            for key, labelEncoder in self.label_dict.items():
                label_detail_dict[key] = dict(zip(labelEncoder.classes_.tolist(), range(0, len(labelEncoder.classes_))))
            with open(self.out_label_detail_path, 'w') as f:
                json.dump(label_detail_dict, f, indent=4)

        else:  # 不需要label_encode,全部为数值型的字段
            # 针对原本是数值型的字段,判断是否需要归一化处理
            if self.dense_feature_type == "minmaxscaler":
                df_dense = df.iloc[:, 1:]
                mms = preprocessing.MinMaxScaler(feature_range=(0, 1))
                mms.fit(df_dense)  # 先适配一下,然后保存下来
                aa = mms.transform(df_dense)
                print(aa)
                # 保存成文件,待预测使用
                joblib.dump(mms, self.mms_save_file)
                df_mms = mms.transform(df_dense)  # 归一化后的dataframe
                pd_stg_input = pd.concat([df[[0]], pd.DataFrame(df_mms)],
                                         axis=1)  # 传入可变参数

                pd_stg_input.to_csv(self.encode_file_path, header=False, index=False,
                                    sep=self.file_separator,
                                    encoding=u'utf-8')

            elif self.dense_feature_type == "log":
                df_dense = df.iloc[:, 1:]
                # 前面数值部分log处理
                for i in range(1, cols_num):
                    df_dense[i] = df_dense[i].apply(lambda x: np.log(x + 1) if x > -1 else -1)

                pd_stg_input = pd.concat([df[[0]], df_dense], axis=1)  # 传入可变参数
                pd_stg_input.to_csv(self.encode_file_path, header=False, index=False,
                                    sep=self.file_separator,
                                    encoding=u'utf-8')

            else:
                # 直接原文件输出
                df.to_csv(self.encode_file_path, header=False, index=False, sep=self.file_separator,
                          encoding=u'utf-8')

    def iv(self):
        # 输出IV值
        iv = toad.IV(self.pd_stg_input.iloc[:, 1:], self.pd_stg_input[:, 0])
        print(iv)

    def _one_label_encode_predict(self, field_index, df):
        """
        单个列,预估数据的转换
        """
        LE = self.label_dict[field_index]  # 获取第几个字段的label_encode
        # df_field = df.iloc[:, field_index].astype('str')  # 要转换类型.astype('str')
        df_field = df.iloc[:, field_index]
        # print(type(df_field))
        # 将新值添加进LE.classes_
        df_field = df_field.map(lambda s: 'unknown' if s not in LE.classes_ else s)
        if not LE.classes_.__contains__('unknown'):
            LE.classes_ = np.append(LE.classes_, 'unknown')
        df_field_enconde_tmp = LE.transform(df_field)
        ############
        df_field_enconde = pd.DataFrame(df_field_enconde_tmp)
        return df_field_enconde

    # def _label_encode_data_predict(self):
    #     """
    #     针对待预测文件的预处理,用已知的label对象重构
    #     """
    #     # 需要转换类型
    #     sparse_feature_dtype = {i: np.dtype('O') for i in
    #                             range(len(self.select_cols) - self.need_label_encode_cols_num - 1,
    #                                   len(self.select_cols) - 1)}
    #
    #     df = pd.read_csv(self.split_cols_file_path, header=None, sep=self.dic_config['file_separator'],
    #                      encoding=u'utf-8', dtype=sparse_feature_dtype)  # 需要指定label的字段的类型
    #
    #     cols_num = df.shape[1]
    #     # df.dropna(axis=0, how='any')  # 删除有nan的行
    #     # 前面数值部分填充0,前提:含有数值的列
    #     if not len(self.select_cols) - 1 == self.need_label_encode_cols_num:
    #         df[[i for i in range(0, cols_num - self.need_label_encode_cols_num)]] = \
    #             df[[i for i in range(0, cols_num - self.need_label_encode_cols_num)]].fillna(0, )
    #
    #     # 后面不是数值的部分填充'-1'
    #     if self.need_label_encode_cols_num:
    #         df[[i for i in range(cols_num - self.need_label_encode_cols_num, cols_num)]] = \
    #             df[[i for i in range(cols_num - self.need_label_encode_cols_num, cols_num)]].fillna('-1')
    #
    #     if self.need_label_encode_cols_num:  # 如果需要label_encode,如果不为0
    #         with open(self.out_label_path, 'rb') as f:
    #             self.label_dict: dict = pickle.load(f)  # 是一个dict,字段映射
    #         # 转换需要转换的字段的list
    #         label_df_list = [*map(lambda index: self._one_label_encode_predict(index, df),
    #                               [x for x in range((0 - self.need_label_encode_cols_num), 0)])
    #                          ]  # -3, -2, -1
    #         if self.need_label_encode_cols_num == len(self.select_cols) -1:  # 全部是需要label_encode字段
    #             pd_stg_input1 = pd.concat([*label_df_list], axis=1)
    #
    #         else:
    #             if self.dense_feature_type == "minmaxscaler":
    #                 df_dense = df.iloc[:, 0: -self.need_label_encode_cols_num]  # 没有label列
    #                 mms = joblib.load(self.mms_save_file)  # MinMaxScaler,数值型字段归一化处理
    #                 df_mms = mms.transform(df_dense)
    #                 pd_stg_input1 = pd.concat([pd.DataFrame(df_mms), *label_df_list], axis=1)
    #             elif self.dense_feature_type == "log":
    #                 df_dense = df.iloc[:, 0: -self.need_label_encode_cols_num]  # 去除lable列
    #                 # 前面数值部分log处理
    #                 for i in range(0, cols_num - self.need_label_encode_cols_num):
    #                     df_dense[i] = df_dense[i].apply(lambda x: np.log(x + 1) if x > -1 else -1)
    #                 pd_stg_input1 = pd.concat([df_dense, *label_df_list], axis=1)
    #
    #             else:  # 不处理
    #                 pd_stg_input1 = pd.concat([df.iloc[:, : -self.need_label_encode_cols_num], *label_df_list],
    #                                          axis=1)  # 传入可变参数
    #
    #     else:  # 如果全部是数值型的字段
    #         if self.dense_feature_type == "minmaxscaler":
    #             mms = joblib.load(self.mms_save_file)  # MinMaxScaler,数值型字段归一化处理
    #             df_mms = mms.transform(df)
    #             pd_stg_input1 = df_mms
    #         elif self.dense_feature_type == "log":
    #             # 前面数值部分log处理
    #             for i in range(0, cols_num):
    #                 df[i] = df[i].apply(lambda x: np.log(x + 1) if x > -1 else -1)
    #                 pd_stg_input1 = df
    #         else:
    #             # 直接原文件输出
    #             pd_stg_input1 = df
    #
    #     pd_stg_input1.to_csv(self.encode_file_path, header=False, index=False,
    #                         sep=self.file_separator,
    #                         encoding=u'utf-8')

    def _label_encode_data_predict(self):
        """
        针对待预测文件的预处理,用已知的label对象重构
        """
        # 需要转换类型
        # sparse_feature_dtype = {i: np.dtype('O') for i in
        #                         range(len(self.select_cols) - self.need_label_encode_cols_num - 1,
        #                               len(self.select_cols) - 1)}

        sparse_feature_dtype = {i: str for i in
                                range(1, self.need_label_encode_cols_num + 1)}

        df = pd.read_csv(self.split_cols_file_path, header=None, sep=self.dic_config['file_separator'],
                         encoding=u'utf-8', dtype=sparse_feature_dtype)  # 需要指定label的字段的类型

        cols_num = df.shape[1]
        # df.dropna(axis=0, how='any')  # 删除有nan的行
        # 前面数值部分填充0,前提:含有数值的列
        # if not len(self.select_cols) - 1 == self.need_label_encode_cols_num:
        #     df[[i for i in range(0, cols_num - self.need_label_encode_cols_num)]] = \
        #         df[[i for i in range(0, cols_num - self.need_label_encode_cols_num)]].fillna(0, )
        # 前面需要编码的字段填充unknown
        df[[i for i in range(0, self.need_label_encode_cols_num + 1)]] = \
            df[[i for i in range(0, self.need_label_encode_cols_num + 1)]].fillna('unknown', )

        # 后面不是数值的部分填充'-1'
        # if self.need_label_encode_cols_num:
        #     df[[i for i in range(cols_num - self.need_label_encode_cols_num, cols_num)]] = \
        #         df[[i for i in range(cols_num - self.need_label_encode_cols_num, cols_num)]].fillna('-1')
        # 后面不需要编码的字段填充0
        if self.need_label_encode_cols_num:
            df[[i for i in range(self.need_label_encode_cols_num + 1, cols_num)]] = \
                df[[i for i in range(self.need_label_encode_cols_num + 1, cols_num)]].fillna(0)

        if self.need_label_encode_cols_num:  # 如果需要label_encode,如果不为0
            with open(self.out_label_path, 'rb') as f:
                self.label_dict: dict = pickle.load(f)  # 是一个dict,字段映射
            # 转换需要转换的字段的list
            # label_df_list = [*map(lambda index: self._one_label_encode_predict(index, df),
            #                       [x for x in range((0 - self.need_label_encode_cols_num), 0)])]  # -3, -2, -1

            label_df_list = [*map(lambda index: self._one_label_encode_predict(index, df),
                                  [x for x in range(1, (self.need_label_encode_cols_num + 1))])]  # -3, -2, -1

            if self.need_label_encode_cols_num == len(self.select_cols) -1:  # 全部是需要label_encode字段
                pd_stg_input1 = pd.concat([*label_df_list], axis=1)

            else:
                if self.dense_feature_type == "minmaxscaler":
                    df_dense = df.iloc[:, 0: -self.need_label_encode_cols_num]  # 没有label列
                    mms = joblib.load(self.mms_save_file)  # MinMaxScaler,数值型字段归一化处理
                    df_mms = mms.transform(df_dense)
                    pd_stg_input1 = pd.concat([pd.DataFrame(df_mms), *label_df_list], axis=1)
                elif self.dense_feature_type == "log":
                    df_dense = df.iloc[:, 0: -self.need_label_encode_cols_num]  # 去除lable列
                    # 前面数值部分log处理
                    for i in range(0, cols_num - self.need_label_encode_cols_num):
                        df_dense[i] = df_dense[i].apply(lambda x: np.log(x + 1) if x > -1 else -1)
                    pd_stg_input1 = pd.concat([df_dense, *label_df_list], axis=1)

                else:  # 不处理
                    # pd_stg_input1 = pd.concat([df.iloc[:, : -self.need_label_encode_cols_num], *label_df_list], axis=1)  # 传入可变参数
                    pd_stg_input1 = pd.concat([*label_df_list, df.iloc[:, self.need_label_encode_cols_num + 1:]], axis=1)

        else:  # 如果全部是数值型的字段
            if self.dense_feature_type == "minmaxscaler":
                mms = joblib.load(self.mms_save_file)  # MinMaxScaler,数值型字段归一化处理
                df_mms = mms.transform(df)
                pd_stg_input1 = df_mms
            elif self.dense_feature_type == "log":
                # 前面数值部分log处理
                for i in range(0, cols_num):
                    df[i] = df[i].apply(lambda x: np.log(x + 1) if x > -1 else -1)
                    pd_stg_input1 = df
            else:
                # 直接原文件输出
                pd_stg_input1 = df

        pd_stg_input1.to_csv(self.encode_file_path, header=False, index=False,
                            sep=self.file_separator,
                            encoding=u'utf-8')
