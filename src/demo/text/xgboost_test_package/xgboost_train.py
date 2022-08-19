#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import xgboost as xgb
import csv
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer


from jieba_segment import JiebaSegment
import logging

class XgboostTrain(object):
    """
    # https://blog.csdn.net/liuchonge/article/details/72614524
    采用Xgboost算法进行分类，要求输入训练数据路径，测试数据路径，数据总类数
    训练数据和测试数据要求均为csv格式，
    第一列为类别（number），
    第二列为文本
    """

    def __init__(self, train_path, test_path, class_number):
        self.train_path = train_path
        self.test_path = test_path
        self.class_number = class_number
        self.weight = (0, 0)
        self.test_weight = (0, 0)
        self.train_content=[]
        self.train_opinion=[]
        self.test_content=[]

    # 读取训练集
    def read_train(self, path):
        with open(path, 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)  # #此处读取到的数据是将每行数据当做列表返回的
            column1 = [row for row in reader] #列表生成式,生成二维数组
        content_train = [i[1] for i in column1] # 第一列为文本内容，并去除列名
        opinion_train = [int(i[0])-1 for i in column1] # 第二列为类别，并去除列名， 从0 开始
        print('数据集有 %s 条句子' % len(content_train))
        train = [content_train, opinion_train]
        return train

    # 对列表进行分词并用空格连接
    def segment_word(self, cont):

        def stop_words():
            stop_words_file = open('../data/chineseStopWords.txt', 'r', encoding='gbk')
            stopwords_list = []
            for line in stop_words_file.readlines():
                stopwords_list.append(line[:-1])
            print("stopwords_list=========================")
            print(stopwords_list)
            print("stopwords_list=========================")
            return stopwords_list

        j = JiebaSegment()
        stopwords_list = stop_words()
        c = []
        for i in cont:
            text = ""
            word_list = j.segment(i)
            for word in word_list:
                if word not in stopwords_list and word != '\r\n':
                    text += word
                    text += ' '
            c.append(text)
        return c

    def load_data(self):
        train = self.read_train(self.train_path)  # 返回二维数组[内容,类型]
        self.train_content = self.segment_word(train[0])
        self.train_opinion = np.array(train[1])     # 需要numpy格式
        print("train data load finished")
        test = self.read_train(self.test_path)  # 返回二维数组 [内容,需要]
        self.test_content = self.segment_word(test[0])
        print('test data load finished')

        print('数据加载完成')

    def train(self):
        vectorizer = CountVectorizer()
        tfidftransformer = TfidfTransformer()
        tfidf = tfidftransformer.fit_transform(vectorizer.fit_transform(self.train_content))
        print(type(tfidf))
        self.weight = tfidf.toarray()
        print(tfidf.shape)

        test_tfidf = tfidftransformer.transform(vectorizer.transform(self.test_content))
        self.test_weight = test_tfidf.toarray()
        print(self.test_weight.shape)
        print("===============")
        print(self.weight)
        print(self.train_opinion)
        print("===============")
        dtrain = xgb.DMatrix(self.weight, label=self.train_opinion)
        param = {'max_depth':6, 'eta':0.5, 'eval_metric':'merror', 'silent':1, 'objective':'multi:softmax', 'num_class':self.class_number}  # 参数
        evallist  = [(dtrain,'train')]  # 这步可以不要，用于测试效果
        num_round = 50  # 循环次数
        print('开始训练模型')
        bst = xgb.train(param, dtrain, num_round, evallist)
        print('模型训练完成')
        return self.test_weight, bst


if __name__ == '__main__':
    xgtrain = XgboostTrain('../data/training.csv', '../data/testing.csv', class_number=11)
    xgtrain.load_data()
    test_weight, bst = xgtrain.train()
    bst.save_model("../data/training.model")
