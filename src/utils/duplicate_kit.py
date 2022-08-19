# coding:utf-8
import sys


class DuplicateKit:
    '''
    重复度过滤
    '''

    def __init__(self):
        pass

    def get_lcs(self, s1, s2):
        '''
        求两个字符串的最长公共子串
        思想：建立一个二维数组，保存连续位相同与否的状态
        '''

        m = [[0 for i in range(len(s2)+1)] for j in range(len(s1)+1)]

        mmax = 0    # 最长匹配长度
        p = 0       # 匹配的起始位

        for i in range(len(s1)):
            for j in range(len(s2)):
                if s1[i] == s2[j]:
                    # 相同则累加
                    m[i+1][j+1] = m[i][j]+1

                    if m[i+1][j+1] > mmax:
                        # 获取最大匹配长度
                        mmax = m[i+1][j+1]

                        # 记录最大匹配长度的终止位置
                        p = i + 1

        return s1[p-mmax:p]

    def title_check_method1(self, news1, news2):
        # 重复的关键词权重之和 / 两个新闻关键词权重之和
        news1_tags = news1['tags_weight']
        news2_tags = news2['tags_weight']

        same_tags = set(news1_tags.keys()) & set(news2_tags.keys())

        if not same_tags:
            return 0

        # 相同关键词的权重之和
        same_tags_sum = 0
        for k in same_tags:
            same_tags_sum += news1_tags[k]
            same_tags_sum += news2_tags[k]

        # 新闻全部关键词的权重之和
        news1_tags_sum = sum(news1_tags.values())
        news2_tags_sum = sum(news2_tags.values())
        return 1.0 * same_tags_sum / (news1_tags_sum + news2_tags_sum)

    def title_check_method2(self, news1, news2):
        # 最长公共子串 / 较短的标题
        lcs = self.get_lcs(news1['title'], news2['title'])
        return 1.0 * len(lcs) / min(len(news1['title']), len(news2['title']))

    def is_duplicate_images(self, news1, news2):
        # 判断缩略图的md5是否重复
        if 'img_md5' in news1 and 'img_md5' in news2:
            if news1['img_md5'] == news2['img_md5']:
                return True
            else:
                return False
        return False

    def is_duplicate_title(self, news1, news2):
        # 判断标题是否重复
        len_news1_title = len(news1['title'])
        len_news2_title = len(news2['title'])
        if len_news1_title <= 10 or len_news2_title <= 10:
            _score1 = self.title_check_method1(news1, news2)
            _score2 = self.title_check_method2(news1, news2)
            score = max(_score1, _score2)
        else:
            score = self.title_check_method1(news1, news2)

        if score > 0.4:
            return True
        else:
            return False

    def is_duplicate(self, news1, news2):
        # 判断两条新闻是否重复
        # 1. 判断缩略图的md5是否重复
        if news1['id'] == news2['id']:
            return True
        if self.is_duplicate_images(news1, news2):
            return True
        # 2. 判断标题是否重复
        if self.is_duplicate_title(news1, news2):
            return True
        return False

    def remove_internal_duplicate(self, news_list):
        # 内部去重
        new_news_list = []
        for i in range(0, len(news_list)):
            is_i_news_duplicate = False
            i_news = news_list[i]
            for j in range(i+1, len(news_list)):
                j_news = news_list[j]
                if self.is_duplicate(i_news, j_news):
                    is_i_news_duplicate = True
                    break

            if not is_i_news_duplicate:
                new_news_list.append(i_news)
        return new_news_list

    def remove_history_duplicate(self, news_list, history_news_list):
        # 和历史新闻去重
        new_news_list = []
        for news in news_list:
            is_news_duplicate = False
            for history_news in history_news_list:
                if self.is_duplicate(news, history_news):
                    is_news_duplicate = True
                    break
            if not is_news_duplicate:
                new_news_list.append(news)
        return new_news_list
