import sys

sys.path.append('../model')
from model.apriori import Apriori
from .base import Base


class Collaborative(Base):
    def __init__(self, dic_config={}):
        Base.__init__(self, dic_config)
        self.file_path = dic_config.pop('data_path')
        self.out_path = dic_config.pop('out_path')
        self.dataSet = self.load_data()
        self.dic_config['dataSet'] = self.dataSet

    def load_data(self):
        dataSet = {}
        f = open(self.file_path, "r", encoding="utf-8")
        for line in f:
            data = line.strip().split("\t")
            user = data[0]
            # print(user)

            del data[0]
            dataSet[user] = data[0].split(',')
        f.close()
        return dataSet

    def write_files(self, res_dict: dict):
        with open(self.out_path, 'w') as f:
            for k, v in res_dict.items():
                v.sort(key=lambda x: x[1], reverse=True)
                topN = v[0:self.dic_config['topk']]
                valueStr = ','.join(map(lambda t: f'{t[0]}:{t[1]}', topN))
                f.write(f'{k}\t{valueStr}\n')

    def run(self):
        apriori = Apriori(self.dic_config)
        return_ = apriori.run()
        self.write_files(return_)
