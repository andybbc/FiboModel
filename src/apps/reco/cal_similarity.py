# -*- coding:utf-8 -*-
import gflags
import sys
sys.path.append("..")

from utils import logs
from train.news_similary import NewSimilary


Flags = gflags.FLAGS
gflags.DEFINE_string('in_file', 'tags-default.json', '新闻标签数据存储文件')
gflags.DEFINE_string('similarity_file', 'news_similarity_range-default.json', '新闻相似度计算结果存储文件')
gflags.DEFINE_string('log_path', 'news-default.log', '日志文件')


dic_config = {}

def init():
    global dic_config
    gflags.FLAGS(sys.argv)

    dic_config["data_path"] = Flags.in_file,
    dic_config["out_path"] = Flags.similarity_file,
    dic_config['logger'] = logs.Logger(log_path=Flags.log_path).logger

def run():
    global dic_config
    logger = dic_config['logger']
    logger.info("=== NewsList TxtSimilarity START ===")

    # 计算新闻相似度
    txt_similarity = NewSimilary(dic_config)
    txt_similarity.run()

    logger.info("=== DONE ===")


if __name__ == '__main__':
    init()
    run()


