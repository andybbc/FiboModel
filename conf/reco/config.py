# coding:utf-8
mongo_conf = {
    'host': '172.16.189.215',
    'port': 27017,
    'timeout': 60000,
    'db': 'cr',
    'col_name': {
        '17': 'news:appnews',
        '18': 'news:mil',
        '20': 'news:cri',
        '21': 'news:china',
        '23': 'news:edn',
    }
}

redis_conf = {
    # 'host': '172.16.189.215',
    'host': '172.16.189.210',
    'port': 6379,
    'timeout': 5,
    'db': 1
}
