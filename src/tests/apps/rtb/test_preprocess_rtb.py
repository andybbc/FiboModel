# -*- coding:utf-8 -*-
import sys
sys.path.append("..")

import json
import utils.keyword_extract as words_utils


def load_data():
    with open("../data/news-list.json", "rb") as f:
        return json.loads(f.read())


def run():
    dset = load_data()
    recom_list = words_utils.kw_top(dset, "伏明霞", 3, 'edn_5e41ca6102d76b2e6b5a3e6b94b285ae')
    print(recom_list)


if __name__ == '__main__':
    run()
