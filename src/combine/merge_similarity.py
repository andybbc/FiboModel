# 合并不同规则的推荐文件

class MergeSimilaryityFile(object):
    def __init__(self, input_file1, input_file2, output_file, rate1, rate2):
        """
        :param input_file1: 输入文件 1,如果是这个文件过来的,标记为1,第一个 1|x
        :param input_file2: 输入文件2,标记为1 ,第二个1 x|1
        :param output_file: 输出文件
        :param rate1: 1文件权重
        :param rate2: 2文件权重
        :return:
        """
        self.input_file1 = input_file1
        self.input_file2 = input_file2
        self.output_file = output_file
        self.rate1 = rate1
        self.rate2 = rate2

    @staticmethod
    def line_to_key_dict(line):
        dict_inner = {}
        arr = line.split("\t")
        key = arr[0]
        value = arr[1]
        arr2 = value.split(",")
        for a in arr2:
            aaa = a.split(":")
            dict_inner[aaa[0]] = float(aaa[1])
        return key, dict_inner

    @staticmethod
    def content_to_dict(file_path):
        dict_outer = {}
        with open(file_path, 'r') as f:
            while True:
                line = f.readline()
                if not line:
                    break
                key, dict_inner = MergeSimilaryityFile.line_to_key_dict(line)
                dict_outer[key] = dict_inner
        return dict_outer

    def merge(self):
        # 文件1到内存,遍历文件2
        dict1 = MergeSimilaryityFile.content_to_dict(self.input_file1)
        with open(self.input_file2) as f:
            with open(self.output_file, 'w') as out_file:
                while True:
                    line = f.readline()
                    if not line:
                        break

                    # 修改dict_inner,第二个文件
                    key2, dict_inner2 = MergeSimilaryityFile.line_to_key_dict(line)

                    if key2 in dict1.keys():  # 如果dict1中包含遍历的key
                        dict_value1 = dict1.pop(key2)  # 拿到dict1的key的值
                        for k, v in dict_inner2.items():
                            if k in dict_value1.keys():
                                dict_inner2[k] = (dict_value1.pop(k) * self.rate1 + v * self.rate2,'1|1')
                            else:
                                dict_inner2[k] = (v * self.rate2,'0|1') # 2有,1没有
                        # 看dict1还有没有数据
                        for k1, v1 in dict_value1.items():
                            dict_inner2[k1] = (v1 * self.rate1, '1|0')

                        sort_list = sorted(dict_inner2.items(), key=lambda d: d[1][0], reverse=True)
                        res_line = ','.join(map(lambda x: f'{x[0]}:{round(x[1][0], 2)}:{x[1][1]}', sort_list))
                        out_file.write(f"{key2}\t{res_line}\n")
                    else:  # 在1中没有,直接加rate修改这个
                        sort_list = sorted(dict_inner2.items(), key=lambda d: d[1], reverse=True)
                        res_line = ','.join(map(lambda x: f'{x[0]}:{round(x[1] * self.rate2, 2)}:0|1', sort_list))
                        out_file.write(f"{key2}\t{res_line}\n")

                # 查看剩下的dict1,追加上去
                for k1, v1 in dict1.items():
                    sort_list = sorted(v1.items(), key=lambda d: d[1], reverse=True)
                    res_line = ','.join(map(lambda x: f'{x[0]}:{round(x[1] * self.rate1, 2)}:1|0', sort_list))
                    out_file.write(f"{k1}\t{res_line}\n")


if __name__ == '__main__':
    mergeSimilaryityFile = MergeSimilaryityFile("../../data/collaborative/aa.txt",
                                                "../../data/collaborative/aa2.txt",
                                                "../../data/collaborative/out3.txt",
                                                0.7,
                                                0.3
                                                )

    mergeSimilaryityFile.merge()
