import csv

from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer

from model.base import Base
from utils.jiebasegment import JiebaSegment
import numpy as np


class segment_words(Base):

    def __init__(self, dic_config: dict):
        super().__init__(dic_config)
        self.dic_config = dic_config
        self.logger = dic_config['logger']
        pass

    # 读取训练集
    def text_read_train(self, path):
        with open(path, 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)  # #此处读取到的数据是将每行数据当做列表返回的
            column1 = [row for row in reader]  # 列表生成式,生成二维数组
        content_train = [i[1] for i in column1]  # 第一列为文本内容，并去除列名
        opinion_train = [int(i[0]) - 1 for i in column1]  # 第二列为类别，并去除列名， 从0 开始
        self.logger.info('数据集有 %s 条句子' % len(content_train))
        train = [content_train, opinion_train]
        return train

    def text_read_test(self,path):
        """ 不带行号,直接一行一个文章 """
        # with open(path, 'r', encoding='utf-8') as csvfile:
        #     lines = csvfile.readlines()
        #     self.logger.info('数据集有 %s 条句子' % len(lines))
        #     return lines

        with open(path,'r',encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            column1 = [row for row in reader]
        content_test = [i[0] for i in column1]
        return content_test

    # 对列表进行分词并用空格连接
    def text_segment_word(self, cont):

        def stop_words():
            stop_words_file = open(self.dic_config['stop_words_path'], 'r', encoding='gbk')
            stopwords_list = []
            for line in stop_words_file.readlines():
                stopwords_list.append(line[:-1])
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

    def text_load_train_data(self):
        train = self.text_read_train(self.dic_config['data_path'])  # 返回二维数组[内容,类型]
        train_content = self.text_segment_word(train[0])
        train_opinion = np.array(train[1])  # 需要numpy格式
        self.logger.info("=== train data load finished ===" )
        self.logger.info('训练数据加载完成')
        return train_content, train_opinion


    def text_load_test_data(self, string=None): #############################################################################
        if string is None:
            test = self.text_read_test(self.dic_config['test_path'])  # 返回二维数组 [内容,需要]
            # print("test ==" * 3)
            # print(test)
            # print("test ==" * 3)
            test_content = self.text_segment_word(test)
            # print("testcontent------------")
            # print(test_content)
            # print("testcontent------------")
            self.logger.info('test data load finished')
            self.logger.info('测试数据加载完成')
            return test_content
        else:
            test_content = self.text_segment_word([string])
            return test_content
