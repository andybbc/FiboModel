# -*- coding:utf-8 -*-
import gflags
import json
import sys
sys.path.append("..")
sys.path.append("../..")

from utils import logs
from model.base import Base
from conf.reco.config import mongo_conf
from dataset.news_data import NewsClass

Flags = gflags.FLAGS
gflags.DEFINE_string('delta_hour', 24, '查询时间间隔，单位：小时')
gflags.DEFINE_string('news_category', '', '新闻分类')
gflags.DEFINE_string('out_file', 'old_news_list-default.json', '新闻数据存储文件')
gflags.DEFINE_string('log_path', 'news-default.log', '日志文件')

dic_config = {
    'source_id': ['ah', 'zhm', 'cri', 'chn', 'edn'],
    'col_name': mongo_conf['col_name']
}


def write_data(out_file, json_str):
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(json_str)


if __name__ == '__main__':
    gflags.FLAGS(sys.argv)
    delta_hour = Flags.delta_hour
    news_category = Flags.news_category
    out_file = Flags.out_file


    # 分内容源获取新闻历史数据
    dic_config = {
        "news_category": news_category,
        "delta_hour": int(delta_hour)
    }
    dic_config['logger'] = logs.Logger(log_path=Flags.log_path).logger

    # 日志
    base = Base(dic_config)
    logger = base.logger

    logger.info("=== GET NewsList START ===")


    news_class = NewsClass(dic_config)
    news_list = news_class.get_news()
    news_class.logger.info("=== NEW_CLASS Query NewsList DONE ===")

    # 存储
    news_json_str = json.dumps(news_list, ensure_ascii=False)
    write_data(out_file, news_json_str)
    logger.info("=== Write NewsList DONE ===")
