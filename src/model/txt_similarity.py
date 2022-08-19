# -*- coding:utf-8 -*-
import sys
import json
import datetime

sys.path.append("..")
import numpy as np
from model.base import Base


class TxtSimilarity(Base):
    '''
    文本相似度分析类
    '''

    def __init__(self, dic_config={}):
        Base.__init__(self, dic_config)

        self.similarity = {}
        self.news_list = {}

    def load_data(self, filepath):
        try:
            with open(filepath, 'rb') as file:
                self.news_list = json.load(file)
        except:
            self.logger.error("TxtSimilarity Load news_file error")


    # 公共分词向量函数
    def kw_vectors(self, news_a, news_b):
        kw_set = list(set(news_a["all_tags"]).intersection(
            set(news_b["all_tags"])))

        kw_a_vc = np.zeros(len(kw_set))
        kw_b_vc = np.zeros(len(kw_set))

        for i in range(len(kw_set)):
            kw_a_vc[i] = news_a["all_tags_weight"].get(kw_set[i])
            kw_b_vc[i] = news_b["all_tags_weight"].get(kw_set[i])

        return kw_a_vc, kw_b_vc

    # 余弦相似度算法
    def cosine(self, vc_a, vc_b):
        return float(np.sum(vc_a * vc_b)) / (np.linalg.norm(vc_a)) * np.linalg.norm(vc_b)

    def cal_similarity(self):
        for news_a in self.news_list:
            self.similarity[news_a['id']] = list()
            for news_b in self.news_list:
                if news_b['id'] == news_a['id']:
                    continue

                # 生成公共分词向量
                vc_a, vc_b = self.kw_vectors(news_a, news_b)

                if len(vc_a) == 0:
                    continue

                # 调用相似度算法
                score = self.cosine(vc_a, vc_b)

                self.similarity[news_a['id']].append(
                    {'news_id': news_b['id'], 'score': score})

            # 排序
            self.similarity[news_a['id']] = sorted(
                self.similarity[news_a['id']],
                key=lambda x: x.get("score"), reverse=True)

        # 保留非空项
        self.similarity = {key: value for key, value in self.similarity.items() if len(value) > 0}