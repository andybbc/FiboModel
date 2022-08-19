import sys
sys.path.append('..')
from model.txt_similarity import TxtSimilarity
from model.base import Base

class NewSimilary(Base):
    def __init__(self, dic_config={}):
        Base.__init__(self, dic_config)
        self.file_path = dic_config.pop('data_path')[0]
        self.out_path = dic_config.pop('out_path')[0]

    def write_data(self, similarity, similarity_file):
        with open(similarity_file, 'w', encoding="utf-8") as file:
            for key, value in similarity.items():
                str = key + "\t"
                for i in range(len(value)):
                    str += "{0}:{1},".format(
                                        value[i]["news_id"],
                                        round(value[i]["score"], 2))
                str = str[:-1] + "\n"

                file.write(str)

    def run(self):
        txt_similarity = TxtSimilarity(self.dic_config)
        txt_similarity.load_data(self.file_path)
        txt_similarity.cal_similarity()
        self.write_data(txt_similarity.similarity, self.out_path)
