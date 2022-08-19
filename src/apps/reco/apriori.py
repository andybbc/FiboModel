# -*- coding:utf-8 -*-
import sys
import gflags

sys.path.append("..")
sys.path.append('../..')

from utils import logs
from train.Collaborative import Collaborative
from conf.reco.apriori import CONFIG

Flags = gflags.FLAGS

gflags.DEFINE_string('data_path', '../../data/demo/test.txt', 'input_file')
gflags.DEFINE_string("out_path", '../../data/collaborative/out.txt', '文件输出路径')
gflags.DEFINE_string("log_path", '../../log/log', '日志输出路径')

dic_config = {}

def init():
    global dic_config
    gflags.FLAGS(sys.argv)

    dic_config.update(CONFIG)

    dic_config['data_path'] = Flags.data_path  # 输入
    dic_config['out_path'] = Flags.out_path  # 文件输出
    dic_config['logger'] = logs.Logger(log_path=Flags.log_path).logger


def run():
    global dic_config
    train = Collaborative(dic_config)
    train.run()


if __name__ == '__main__':
    init()
    run()
