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




