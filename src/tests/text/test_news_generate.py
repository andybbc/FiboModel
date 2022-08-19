# -*- coding:utf-8 -*-
import sys
sys.path.append("..")
from model.txt_similarity import TxtSimilarity
from model.keyword_extract import KWExtract
from preprocess.news_list import NewsList
from generate.dftt_news import DFTT
import datetime
import json


def write_data(json_str=""):
    file = "../../data/raw/news_list-{0}.json".format(datetime.date.today())
    with open(file, "w", encoding="utf-8") as f:
        f.write(json_str)


def run():
    # 获取新闻数据
    dftt = DFTT(page=2)
    dftt.gen_news()
    news_source = dftt.news_source
    print('get news_list count:', len(news_source["news"]))

    # 新闻数据深加工
    newslist = NewsList(news_source["news"], news_source["prefix"])
    newslist.process()
    print("NewsList Process done.")

    # 存储
    # newslist.save2db()

    # 本地数据
    write_data(json.dumps(newslist.news_list, ensure_ascii=False))
    print("NewsList write done.")

    # 中文分词，生成关键字标签
    wk_extract = KWExtract()
    if not hasattr(wk_extract, 'news_list'):
        return

    wk_extract.gen_tags()
    wk_extract.news_update()

    # 计算文章相似度
    txt_similarity = TxtSimilarity()
    if not hasattr(txt_similarity, 'news_list'):
        return

    txt_similarity.cal_similarity()
    print("Similarity calculate done.")

    txt_similarity.write_data()
    print("Similarity write done.")


if __name__ == '__main__':
    run()
