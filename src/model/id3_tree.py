# -*- coding:utf-8 -*-
import pandas as pd
from math import log


# 信息熵计算函数
from model.base import Base


def entropy(ele):
    '''
        entropy = - sum(p * log(p)), p is a prob value.
    '''
    # set(ele) 特征值集合
    # probs    特征值比率
    probs = [ele.count(i) / len(ele) for i in set(ele)]
    entropy = -sum([prob * log(prob, 2) for prob in probs])
    return entropy


# 根据特征和特征值划分数据集函数
def split_dataframe(data, col):
    # 特征值数组
    unique_values = data[col].unique()
    
    result_dict = {elem: pd.DataFrame for elem in unique_values}
    
    for key in result_dict.keys():
        result_dict[key] = data[:][data[col] == key]
    
    return result_dict


# 根据熵计算公式和数据集划分方法计算信息增益选择最佳特征
def choose_best_col(data, label):
    # 结果集的熵
    entropy_D = entropy(data[label].tolist())
    
    # 特征集(不包括结果)列表
    cols = [col for col in data.columns if col not in [label]]
    
    # 计算信息增益最大值及对应特征
    max_value, best_col = -999, None
    max_splited = None
    
    for col in cols:
        # 创建每个特征值的分类标签
        splited_set = split_dataframe(data, col)
        
        entropy_DA = 0
        for subset_col, subset in splited_set.items():
            # 按照特征值分类后的信息熵
            entropy_Di = entropy(subset[label].tolist())
            
            entropy_DA += len(subset) / len(data) * entropy_Di
            
        # 信息增益
        info_gain = entropy_D - entropy_DA

        # 信息增益越大，表示该特征对数据有较强的分类能力
        if info_gain > max_value:
            max_value, best_col = info_gain, col
            max_splited = splited_set
            
    return max_value, best_col, max_splited


class ID3Tree(Base):
    class Node:
        # 节点类
        def __init__(self, name):
            self.name = name
            self.connections = {}

        def connect(self, label, node):
            self.connections[label] = node

    def __init__(self, dic_config):
        Base.__init__(self, dic_config)
        self.label = dic_config.get('label')
        self.root = self.Node("Root")   # 根节点

    def print_tree(self, node, tabs):
        print(tabs + node.name)
        for connection, child_node in node.connections.items():
            print(tabs + "\t" + "(" + connection + ")")
            self.print_tree(child_node, tabs + "\t\t")

    def construct_tree(self, data):
        
        self.columns = data.columns
        self.data = data
        
        self.construct(self.root, "Root", self.data, self.columns)

    def construct(self, parent_node, parent_connection_label, input_data, columns):
        # 计算信息增益最大值及特征数据集
        max_value, best_col, max_splited = choose_best_col(input_data[columns], self.label)
        if not best_col:
            node = self.Node(input_data[self.label].iloc[0])
            parent_node.connect(parent_connection_label, node)
            return

        node = self.Node(best_col)
        parent_node.connect(parent_connection_label, node)

        new_columns = [col for col in columns if col != best_col]

        for splited_value, splited_data in max_splited.items():
            self.construct(node, splited_value, splited_data, new_columns)
     
    def store_tree(self, inputTree, filename):
        import pickle
        fw = open(filename, 'wb')
        pickle.dump(inputTree, fw)
        fw.close()
