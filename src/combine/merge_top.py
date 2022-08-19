# 实现合并top和推荐的文件
import sys


class FileMerge(object):
    # 最小值
    __min_num = float(- sys.maxsize - 1)

    def __init__(self, collaborative_file, topn_file, out_file):
        self.collaborative_file = collaborative_file
        self.topn_file = topn_file
        self.out_file = out_file

    @staticmethod
    def origin_line_to_dict(line: str):
        '''原始数据切成dict'''
        result = {}
        for kv in line.split(","):
            arr = kv.split(":")
            result[arr[0]] = (float(arr[1]), arr[2])
        return result

    def ref_line_to_dict(self):
        '''topN切成dict'''
        result = {}
        with open(self.topn_file, 'r') as f:
            list = f.readlines()
            for kv in list:
                arr = kv.split(",")
                result[arr[0]] = arr[1].replace('\n','')

        return result

    @staticmethod
    def transform_tuple(tuple1):
        return f'{tuple1[0]}:{tuple1[1][0][0]}:{tuple1[1][0][1]}'

    @staticmethod
    def generate_str(t, other):
        return

    def merge(self):
        # 参考的dict
        ref_dict = self.ref_line_to_dict()
        with open(self.out_file, 'w') as out_f:
            with open(self.collaborative_file) as f:
                while True:
                    content = f.readline()
                    if not content:
                        break
                    arr = content.split("\t")
                    user = arr[0]
                    refs = arr[1].replace("\n",'')
                    ori_dict = FileMerge.origin_line_to_dict(refs)
                    for k, v in ori_dict.items():
                        ori_dict[k] = (v, ref_dict.get(k, self.__min_num))

                    list_sorted = sorted(ori_dict.items(), key=lambda d: (float(d[1][1]), d[1][0][0]), reverse=True)
                    result_list = map(FileMerge.transform_tuple, list_sorted)
                    result_str = ','.join(result_list)
                    out_f.write(user + "\t" + result_str + "\n")