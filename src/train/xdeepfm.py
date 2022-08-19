from sklearn.model_selection import train_test_split

from model.base import Base
from deepctr.feature_column import SparseFeat, DenseFeat, get_feature_names
import pandas as pd
from keras.models import load_model, save_model
from model.xdeepfm import XDeepFMModel


class XDeepFMTrain(Base):
    def __init__(self, dic_config):
        super().__init__(dic_config)

        self.dic_config = dic_config
        self.logger = dic_config['logger']

        self.encode_file_path = dic_config['encode_file_path']  # 可以用于模型的文件,label后的文件
        self.need_label_encode_cols_num = dic_config['need_label_encode_cols_num']  # 区分SparseFeature和DenseFeature
        # 输出的model的路径
        self.xdeepfm_model_path = dic_config['xdeepfm_model_path']

    def load_data_and_get_feature_names(self):
        '''
        已经是预处理之后的文件了,但是还是要区分SparseFeature和DenseFeature
        :return:
        '''

        self.df_train = pd.read_csv(self.encode_file_path, header=None, sep=self.dic_config['file_separator'],
                                    encoding=u'utf-8')
        cols_num = self.df_train.shape[1]

        # 要指定名字
        # columns_name = []
        # columns_name.append('label')
        # sparse_features = ['C' + str(i) for i in range(1, self.need_label_encode_cols_num + 1)]
        # dense_features = ['I' + str(i) for i in range(1, cols_num - self.need_label_encode_cols_num)]
        # columns_name.extend(dense_features)
        # columns_name.extend(sparse_features)
        # self.df_train.columns = columns_name
        self.df_train.columns = [str(i) for i in range(0, cols_num)]  # 按照下标建名字

        # 后面的散列的字段
        # aa =[ i for i in range(cols_num - self.need_label_encode_cols_num, cols_num)]
        # sparse_feature_columns = [SparseFeat(str(i), vocabulary_size=self.df_train[[i]].nunique().values[0], embedding_dim=4)
        #                           for i in range(cols_num - self.need_label_encode_cols_num, cols_num)]
        sparse_feature_columns = [
            SparseFeat(str(i), vocabulary_size=self.df_train[str(i)].nunique(), embedding_dim=4)
            for i in range(cols_num - self.need_label_encode_cols_num, cols_num)]
        # sparse_feature_columns = [SparseFeat(feat, vocabulary_size=self.df_train[feat].nunique(), embedding_dim=4)
        #                           for i, feat in enumerate(sparse_features)]
        # 前面的数值的字段
        # dense_feature_columns = [DenseFeat(str(i), 1, )
        #                          for i in range(1, cols_num - self.need_label_encode_cols_num)]
        dense_feature_columns = [DenseFeat(str(i), 1, )
                                 for i in range(1, cols_num - self.need_label_encode_cols_num)]
        # dense_feature_columns = [DenseFeat(feat, 1, ) for feat in dense_features]

        fixlen_feature_columns = sparse_feature_columns + dense_feature_columns

        dnn_feature_columns = fixlen_feature_columns
        self.dic_config['dnn_feature_columns'] = dnn_feature_columns
        linear_feature_columns = fixlen_feature_columns
        self.dic_config['linear_feature_columns'] = linear_feature_columns

        self.feature_names = get_feature_names(linear_feature_columns + dnn_feature_columns)

    def train(self):
        # 看是不是dev
        if self.dic_config['preprocess_config']['common']['dev'] == True:
            # 是dev的情况就拆分
            train, test = train_test_split(self.df_train, test_size=0.2, random_state=2018)
            train_model_input = {name: train[name] for name in self.feature_names}
            test_model_input = {name: test[name] for name in self.feature_names}  #
            dfm = XDeepFMModel(self.dic_config)
            model = dfm.train(train_model_input, train.iloc[:, 0:1].values)
            save_model(model, self.xdeepfm_model_path)

        else:
            train_model_input = {name: self.df_train[name] for name in self.feature_names}
            dfm = XDeepFMModel(self.dic_config)
            model = dfm.train(train_model_input, self.df_train.iloc[:, 0:1].values)
            save_model(model, self.xdeepfm_model_path)


