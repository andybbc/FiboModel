# coding:utf-8
from redis import Redis
import sys
sys.path.append("../..")
from conf.reco.config import redis_conf
from conf.reco.category import SourceMap
import random
import string
import time

LIST_INSERT_SCRIPT = """
local lkey = KEYS[1]
local zkey = 'vof:' .. lkey
local score, member = KEYS[2], KEYS[3]
redis.call('LPUSH', lkey, unpack(ARGV))
redis.call('ZADD', zkey, score, member)
redis.call('ZREMRANGEBYSCORE', zkey, 0, tonumber(score)-3600000)
"""

KEY_PREFIX_DICT = {
    "17": "appnews",
    "18": "mil",
    "20": "cri",
    "21": "chn",
    "23": "edn",
}


class RedisKit:
    def __init__(self, newsid_prefix):
        self.red = Redis(
            host=redis_conf['host'],
            port=redis_conf['port'],
            db=redis_conf['db'],
            socket_timeout=redis_conf['timeout'],
            decode_responses=True
        )

        source_id = newsid_prefix
        if newsid_prefix in SourceMap:
            source_id = SourceMap[newsid_prefix]

        key_prefix = KEY_PREFIX_DICT[source_id]
        print('key_prefix:', key_prefix)

        self.list_max = 10000
        self.tag_max = 100
        self.home_key = key_prefix + ':r:home'
        self.chn_key_prefix = key_prefix + ':r:c:'
        self.tag_key_prefix = 'tag:%s:' % source_id
        self.top_key_prefix = 'TopN:'     # 按点击排序
        self.range_key_prefix = 'Range:'  # 按算法结果排序
        self.list_insert_eval = self.red.register_script(LIST_INSERT_SCRIPT)

    def is_news_uploaded(self, news_id):
        key = 'h:n:' + news_id
        return self.red.exists(key)

    def save_uploaded_newsid(self, news_id):
        key = 'h:n:' + news_id
        self.red.set(key, '1')
        self.red.expire(key, 3600*24*3)

    def _save_news_list(self, key, news_id_list):
        old_id_list = self.red.lrange(key, 0, -1)
        # 去重
        news_id_list = list(set(news_id_list) - set(old_id_list))

        # 空
        if not news_id_list:
            return

        # 为保证分批插入的顺序，逆转两次
        news_id_list.reverse()
        for i in range(0, len(news_id_list), 50):
            # args
            slice_list = news_id_list[i:i+50]
            # keys
            score = str(int(time.time()*1000))
            rand = ''.join(random.sample(string.letters, 5))
            member = rand + ':' + str(len(slice_list))
            # 执行脚本
            self.list_insert_eval(
                    keys=[key, score, member],
                    args=slice_list,
                )
        # 保留最大长度
        self.red.ltrim(key, 0, self.list_max)

    def save_home_news_list(self, home_news_list):
        if not home_news_list:
            return
        # 推荐列表
        news_id_list = []
        for news in home_news_list:
            if 'detail' not in news or not news['detail']:
                continue
            news_id_list.append(news['id'])

        self._save_news_list(self.home_key, news_id_list)

    def save_chn_news_list(self, news_list):
        # 分频道取出
        chn_news_id_list = {}
        for news in news_list:
            if 'detail' not in news or not news['detail']:
                continue
            cat = news['cat']
            if cat not in chn_news_id_list:
                chn_news_id_list[cat] = []
            chn_news_id_list[cat].append(news['id'])

        # 分频道存
        for cat in chn_news_id_list:
            key = self.chn_key_prefix + cat
            self._save_news_list(key, chn_news_id_list[cat])

    def _save_tag_list(self, key, tag_newsid_list, list_max):
        old_tag_newsid_list = self.red.lrange(key, 0, -1)
        tag_newsid_list = list(set(tag_newsid_list) - set(old_tag_newsid_list))
        if not tag_newsid_list:
            return

        tag_newsid_list.reverse()
        for i in range(0, len(tag_newsid_list), 50):
            self.red.lpush(key, *tag_newsid_list[i:i+50])

        # 删掉最大长度之后的
        self.red.ltrim(key, 0, list_max)
        # 过期时间为15天
        self.red.expire(key, 1296000)

    def save_tag_list(self, news_list, ):
        # 分频道:标签取出
        tag_newsid_list = {}
        for news in news_list:
            for tag in news['tags']:
                suffix = news['cat'] + ':' + tag
                if suffix not in tag_newsid_list:
                    tag_newsid_list[suffix] = []
                tag_newsid_list[suffix].append(news['id'])

        # 存
        for tag in tag_newsid_list:
            key = self.tag_key_prefix + tag
            self._save_tag_list(key, tag_newsid_list[tag], self.tag_max)

    def save_topn_list(self, top_file, category_flag):
        # load top 文件，输出行数据数组
        data = []
        with open(top_file, 'r') as f:
            data = f.read()

        data = data.split('\n')

        data = [d.split(',')[0] for d in data]

        # 格式化 key
        key = self.top_key_prefix + category_flag
        self._save_tag_list(key, data, 1000)

    def save_range_list(self, range_file):
        # load range 文件，输出行数据数组
        # news_id1\tnews_id2:weight:1|1
        data = []
        with open(range_file, 'r') as f:
            data = f.read()
        data = data.split('\n')

        for i in range(len(data)):
            row_arr = data[i].split('\t')
            if not row_arr or len(row_arr) < 2:
                continue

            news_id, range_str = row_arr[0], row_arr[1]
            range_arr = [n.split(':')[0] for n in range_str.split(',')]

            # 格式化 key
            key = self.range_key_prefix + news_id
            self._save_tag_list(key, range_arr, 100)
