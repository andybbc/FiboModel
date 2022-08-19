# -*- coding:utf-8 -*-
import gflags
import json
import sys
sys.path.append("..")
from model.base import Base
from model.keyword_extract import KWExtract
from utils import logs

Flags = gflags.FLAGS
gflags.DEFINE_string('in_file', 'old_news_list-default.json', '新闻数据存储文件')
gflags.DEFINE_string('out_file', 'tags-default.json', '新闻数据存储文件')
gflags.DEFINE_string('log_path', 'news-default.log', '日志文件')


def news_update(out_file, json_str):
    try:
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(json_str)
    except:
        logger.error("Update news_file error")


if __name__ == '__main__':
    gflags.FLAGS(sys.argv)
    in_file = Flags.in_file
    out_file = Flags.out_file
    log_path = Flags.log_path

    # base = Base({"logger": logger})

    logger = logs.Logger(log_path=Flags.log_path).logger
    logger.info("=== GEN Tag START ===")

    # 中文分词，生成标签权重数组
    dic_config = {
        "in_file": in_file,
        "log_path": log_path
    }
    dic_config['logger'] = logger  # 日志
    wk_extract = KWExtract(dic_config)
    tags_list = wk_extract.gen_tags()

    # 更新
    news_json_str = json.dumps(tags_list, ensure_ascii=False)
    news_update(out_file, news_json_str)
    logger.info("=== UPDATE NewsList DONE ===")
