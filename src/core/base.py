# -*- coding: utf-8 -*-


class RecoBase():
    logger = None
    dic_config = {}

    def __init__(self, dic_config={}):
        self.dic_config = dic_config
        self.logger = dic_config['logger']
