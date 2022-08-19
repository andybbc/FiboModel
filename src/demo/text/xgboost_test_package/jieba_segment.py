# -*- coding:utf-8 -*-
import jieba
import jieba.analyse
import jieba.posseg as pseg


class JiebaSegment(object):

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


    def keyword(self, string, topK):

        '''提取关键词，返回关键词的list,topK为关键词个数'''
        keyword_list = jieba.analyse.extract_tags(string, topK)

        return keyword_list


if __name__ == '__main__':
    j = JiebaSegment()
    test_string = '距离除夕越来越近，这几天，铁路部门迎来了返乡客流的最高峰。然而，仍有些人，为买不到返乡的车票发愁。某些热门线路，为什么12306总是显示没票可卖?第三方抢票软件到底能不能顺利抢到票?铁路售票平台有没有更多的渠道向社会开放?'
    j.addword('距离除夕越来越近') #增加词
   # j.loaddict('test.txt')  # 增加词
    print('jieba分词结果为：', j.segment(test_string)) #不输出词性
    print("=" * 10)
    print('jieba分词结果（带词性）为：', j.segment(test_string, part_of_speech=True))  # 输出词性
    print("=" * 10)
    print('jieba分词结果为（停用词）：', j.segment(test_string, stop_words=['距离除夕越来越近', '这', '几天']))  # 测试停用词
    print("=" * 10)
    print('jieba关键词提取结果为：', j.keyword(test_string, 10)) # 10为关键词个数