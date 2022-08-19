# coding:utf-8
from pymongo import MongoClient
from conf.reco.category import SourceMap
from conf.reco.config import mongo_conf
import time


class MongoKit:
    def __init__(self, newsid_prefix):
        mgo = MongoClient(
            mongo_conf['host'],
            mongo_conf['port'],
            socketTimeoutMS=mongo_conf['timeout'],
        )

        source_id = SourceMap[newsid_prefix]

        db_name = mongo_conf['db']
        col_name = mongo_conf['col_name'][source_id]
        self.col = mgo[db_name][col_name]

    def save(self, news):
        # 存在更新
        # 不存在插入
        # upsert = True
        try:
            news['created_at'] = int(time.time())
            update = self.col.update({"id": news['id']}, news, True)
            # return update['nModified']
            return True
        except:
            pass

    def get_old_news(self, offset):
        old_news = []
        now = int(time.time())
        values = self.col.find({"created_at": {"$gte": now - offset}})
        for v in values:
            news = {
                    'id': v['id'],
                    'title': v['title'],
                    'tags_weight': v['tags_weight'],
                    }
            if 'img_md5' in v:
                news['img_md5'] = v['img_md5']
            else:
                news['img_md5'] = []
            old_news.append(news)
        return old_news

    def copy_old_news(self, offset, cat):
        old_news = []
        now = int(time.time())
        query_params = {"created_at": {"$gte": now - offset}}
        if cat:
            query_params = {
                '$and': [
                    {"created_at": {"$gte": now - offset}},
                    {"cat": cat}
                ]
            }
        values = self.col.find(query_params)
        for v in values:
            news = {
                'cat': v['cat'],
                'title': v['title'],
                'source': v['source'],
                'update': v['update'],
                'images': v['images'],
                'raw_url': v.get('raw_url'),
                'detail': v['detail'],
                'tags_weight': v['tags_weight'],
                'id': v['id'],
                'tags': v['tags'],
                'detail_tags': v.get('detail_tags')
            }
            old_news.append(news)
        return old_news
