# -*- coding:utf-8 -*-
import datetime
import gflags
import sys
sys.path.append("..")
sys.path.append("../..")
from model.base import Base
from utils.redis_kit import RedisKit
from utils import logs

Flags = gflags.FLAGS
gflags.DEFINE_string('range_file', 'news_similarity_range-default.json', '算法排序结果文件')
gflags.DEFINE_string('log_path', 'news-default.log', '日志文件')

if __name__ == '__main__':
    gflags.FLAGS(sys.argv)
    range_file = Flags.range_file
    log_file = Flags.log_file

    logger = logs.Logger(log_path=Flags.log_path).logger

    logger.info("=== START ===")
    redis_client = RedisKit("edn")

    # 写入算法排序数据
    redis_client.save_range_list(range_file)

    logger.info("=== DONE ===")
