# -*- coding:utf-8 -*-
import sys
import json
import datetime
sys.path.append("..")
import jieba
import jieba.analyse as ja
import jieba.posseg as pseg
from model.base import Base


class KWExtract(Base):
    """
    中文分词工具集
    """

    def __init__(self, dic_config={}):
        Base.__init__(self, dic_config)

        self.POSs = ('n', 'ns', 'nsf', 'nr', 'nr2', 'nrf', 'nt', 'nz')
        self.news_file = dic_config.pop('in_file')
        self.load_data()

    def load_data(self):
        try:
            with open(self.news_file, 'rb') as file:
                self.news_list = json.load(file)
        except:
            self.logger.error("KWExtract Load news_file error")

    def extract_tags(self, s, topK=3):
        # 按 TF / IDF 计算关键字权重
        return dict(ja.extract_tags(s, topK=topK, withWeight=True, allowPOS=self.POSs))

    def kw_top(self, kw, topK=10, nid=""):
        self.load_data()
        if not self.news_list:
            return

        # 获取数据集中关键字权重最高的Top10
        # keywords in 查询
        dataset = [news for news in self.news_list if (kw in news.get("tags")) & (nid != news.get("id"))]

        # 按权重排序
        sorted(dataset, key=lambda x: x.get("all_tags_weight")[kw], reverse=True)

        return dataset[:topK]

    def segment(self, string, part_of_speech=False, stop_words=[]):
        '''
        对文章进行分词的函数
        :param string: 传入一个字符串
        :param part_of_speech:  控制词性的输出， False不输出词性，True输出词性，默认不输出
        :return:返回分词结果的list
        '''
        word_list = []
        for w in pseg.cut(string):
            if w.word not in stop_words:
                if part_of_speech:
                    word_list.append([w.word, w.flag])
                else:
                    word_list.append(w.word)

        return word_list

    def addword(self, word):
        jieba.add_word(word)

    def loaddict(self, user_dict):
        jieba.load_userdict(user_dict)

    def gen_tags(self):
        tags_list = list()
        for news in self.news_list:
            # 标题标签提取
            title_tags_dict = self.extract_tags(news['title'], topK=3)
            title_tags = list(title_tags_dict.keys())
            news['tags_weight'] = title_tags_dict
            news['tags'] = title_tags

            # 正文标签提取
            detail_text = []
            for line in news['detail']:
                if type(line) == 'str':
                    detail_text.append(line)
            detail_text = '\n'.join(detail_text)
            detail_tags_dict = self.extract_tags(news['title'], topK=20)
            detail_tags = list(detail_tags_dict.keys())
            news['detail_tags'] = detail_tags

            tag_obj = dict()
            tag_obj['all_tags_weight'] = {**detail_tags_dict, **title_tags_dict}
            tag_obj['all_tags'] = list(set(title_tags + detail_tags))
            tag_obj['id'] = news['id']

            tags_list.append(tag_obj)

        return tags_list
