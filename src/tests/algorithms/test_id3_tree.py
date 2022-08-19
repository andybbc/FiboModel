# -*- coding:utf-8 -*-

import sys

import gflags

sys.path.append("..")

import pandas as pd
from model.id3_tree import ID3Tree as ID3Model
from predict.id3_tree import ID3Tree as ID3Predict
from utils import logs

dic_config = {
    'label': 'play', # 结果集标签
    'model_path': '../data/id3_tree_storage.txt'
}

Flags = gflags.FLAGS

gflags.DEFINE_string("log_path", '../../log/log', '日志输出路径')

def train():
    # 加载数据集
    df = pd.read_csv('../data/id3_example_data.csv', dtype={'windy':'str'})

    # 加载模型
    model = ID3Model(dic_config)

    # 构建决策树
    model.construct_tree(df)

    # 打印决策树
    model.print_tree(model.root, '')
    
    # 存储决策树
    model.store_tree(model, dic_config.get('model_path'))


def predict():
    print("=== Predict ===")

    # 加载数据集
    df_test = pd.read_csv('../data/id3_test_data.csv', dtype={'windy':'str'})
    
    model = ID3Predict(dic_config)
    
    # 加载决策树    
    my_tree = model.load_model(dic_config.get('model_path'))
    
    model.predict(df_test, my_tree.root)


if __name__ == '__main__':
    dic_config['logger'] = logs.Logger(log_path=Flags.log_path).logger
    train()
    predict()
