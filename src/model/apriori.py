import collections
import sys

from .base import Base

class Apriori(Base):
    def __init__(self, dic_config):
        Base.__init__(self, dic_config)

        self.support = dic_config['support']
        self.confidence = dic_config['confidence']
        self.slice = dic_config['topk']
        self.dataSet = dic_config['dataSet']
        self.logger.info(f"""=====Apriori算法 =====
                            支持度:{self.support}
                            置信度:{self.confidence}
                            topk :{self.slice}
                          """)

    # 计算k=1时的支持度，返回符合支持度和不符合支持度，类型为字典，key=item_name,value=item_count
    def cut_tree(self, data_count, data_num, support):
        data = {content: num for content, num in data_count.items() if (num * 1.0 / data_num) >= support}  # 第一次剪枝

        data_cut = {content: num for content, num in data_count.items() if (num * 1.0 / data_num) < support}  # 第一次剪枝
        return data, data_cut

    # 计算k个项的组合项集，利用递归的思想
    def Combinations(self, data, k):
        n = len(data)
        result = []
        for i in range(n - k + 1):
            if k > 1:
                newL = data[i + 1:]
                Comb = self.Combinations(newL, k - 1)
                for item in Comb:
                    item.insert(0, data[i])
                    result.append(item)
            else:
                result.append([data[i]])

        return result

    # 获取k个元素的组合项集，除去k-1不符合支持度的子集（这个值通过剪枝得到）
    def move_cut(self, data, data_cut, K):
        '''

        :param data: xxx项集的数据{'Mix3': 3, 'mate20': 2, 'P20': 3, 'nexs': 3}
        :param data_cut: 被剪枝掉的项集 {'nexs、mate20': 1, 'mate20、P20': 1}, 多项用、分割
        :param K:  xx项集
        :return:
        '''
        content = []
        content_move = []
        for key, value in data.items():
            content += key.split("、")

        content = list(set(list(content)))
        data_list = self.Combinations(content, K)  # 获取子集
        if len(data_list) == 0:
            return data

        for key, value in data_cut.items():
            content_move.append(key.split("、"))

        for i in content_move:
            for j in data_list:
                if set(list(i)).issubset(list(j)):
                    data_list.remove(j)

        return data_list

    # 计算组合项集中的元素在用户-物品倒排表当中出现的次数，主要用于计算支持度
    def num_count(self, dataSet, data):
        data_list = collections.OrderedDict()
        for user, content in dataSet.items():
            content = list(content)
            for i in data:
                if set(list(i)).issubset(list(content)):
                    keys = "、".join(list(i))
                    data_list.setdefault(keys, 0)
                    data_list[keys] += 1

        return data_list

    # 计算所有用户items的购买次数，返回一个字典，key=item_name,value=item_count，其实就是k=1时的num_count
    def first_num_count(self, dataSet):
        data_list = dict()
        for user, content in dataSet.items():
            for keys in content:
                data_list.setdefault(keys, 0)
                data_list[keys] += 1

        return data_list

    # 调用方法
    def first_cut(self):
        '''
        第一次剪枝,
        :param apiori:
        :param support:
        :return:
        '''
        # self.logger.info("用户-新闻内容倒排列表: ", dataSet)

        # 获取所有用户items的购买次数,返回 item,count(出现次数) 的一个dict,wordcount
        data_count = self.first_num_count(self.dataSet)
        # self.logger.info("第1次剪枝前拓展项计数: ", data_count)  # {'Mix3': 3, 'XR': 1, 'mate20': 2, 'P20': 3, 'nexs': 3}

        # 获取用户数目
        data_num = len(self.dataSet)
        # self.logger.info(data_num)
        # 物品的项集为1时，根据支持度进行剪枝,一项集,返回 剪枝后的数据和 被抛弃的数据
        data, data_cut = self.cut_tree(data_count, data_num, self.support)
        # self.logger.info("第1次剪枝后拓展项计数: ", data)
        return data, data_cut, data_num

    def later_cut(self, data, data_cut, data_num):
        '''
        只计算二项集的支持度
        :param apiori:
        # :param dataSet: 原始数据 {'A': ['Mix3', 'XR', 'mate20'], 'B': ['Mix3', 'P20', 'nexs'], 'C': ['Mix3', 'P20', 'nexs', 'mate20'], 'D': ['P20', 'nexs']}
        :param data:     检点后剩余满足支持度的数据 dict  {'Mix3': 3, 'mate20': 2, 'P20': 3, 'nexs': 3}
        :param data_cut: 被剪掉的数据 dict
        :param data_num: 原始数据的条数
        :param support:  支持度
        :return:  [OrderedDict([('P20', 3), ('nexs', 3), ('P20、nexs', 3)]), OrderedDict([('nexs', 3), ('P20', 3), ('P20、nexs', 3)])]

        '''
        # 将物品的项集置为2
        K = 2

        # 获取k个元素的组合项集，除去k-1不符合支持度的子集：data_cut
        data = self.move_cut(data, data_cut, K)
        # self.logger.info("第%d次拓展初始集合: %s" % (K, data))  # data:[['nexs', 'Mix3'], ['nexs', 'mate20'], ['nexs', 'P20'], ['Mix3', 'mate20'], ['Mix3', 'P20'], ['mate20', 'P20']]
        # 计算组合项集中每个元素在用户-物品倒排表当中出现的次数
        data_count = self.num_count(self.dataSet,
                                    data)  # OrderedDict([('Mix3、mate20', 2), ('nexs、Mix3', 2), ('nexs、P20', 3), ('Mix3、P20', 2), ('nexs、mate20', 1), ('mate20、P20', 1)])
        # self.logger.info("第%d次剪枝前拓展项计数: %s" % (K, data_count))

        # 剪枝，剪去不满足支持度的项
        data, data_cut = self.cut_tree(data_count, data_num, self.support)
        # self.logger.info("第%d次剪枝后拓展项计数: %s" % (K, data))
        # self.logger.info("第%d次被剪枝数据: %s" % (K, data_cut))

        # self.logger.info('二项集支持度的数据为:', data)  # {'mate20、Mix3': 2, 'Mix3、nexs': 2, 'Mix3、P20': 2, 'nexs、P20': 3}
        return data

    def compute_confidence(self, data):
        '''
        各个置信度计算
        :param data:  '最后的拓展项集为:'  #例子:  {'mate20、Mix3': 2, 'nexs、Mix3': 2, 'nexs、P20': 3, 'Mix3、P20': 2}
        :return:
        '''
        confidence_dict = {}
        for key, value in data.items():  # 遍历二项集
            content = key.split("、")
            num = value

            # 获取列表的非空子集
            data_num = []
            for i in range(1, len(content)):
                data_num += self.Combinations(content, i)

            # self.logger.info("非空子集data_num:", data_num)  # [['nexs'], ['P20']]
            # self.logger.info("dataSet:", self.dataSet)  # {'A': ['Mix3', 'XR', 'mate20'], 'B': ['Mix3', 'P20', 'nexs'], 'C': ['Mix3', 'P20', 'nexs', 'mate20'], 'D': ['P20', 'nexs']}

            conf_data = {}
            # 置信度计算
            for i in data_num:  # [['Mix3'], ['P20']]
                another = [ii for ii in data_num if ii != i][0][0]
                count = 0
                for u, v in self.dataSet.items():  # {'A': ['Mix3', 'XR', 'mate20'], 'B': ['Mix3', 'P20', 'nexs'], 'C': ['Mix3', 'P20', 'nexs', 'mate20'], 'D': ['P20', 'nexs']}
                    if set(i).issubset(v):
                        count += 1
                        conf_data.setdefault(i[0], ())
                        conf_data[i[0]] = (another, round((float(num) / count), 2))  # 返回一个元组

            # 筛选掉不符合置信度的选项
            new_conf_data = {conf: num for conf, num in conf_data.items() if num[1] >= self.confidence}

            # self.logger.info('符合置信度的项集:', new_conf_data)  # {'nexs': ('Mix3', 0.6666666666666666), 'Mix3': ('nexs', 0.6666666666666666)}
            for k, v in new_conf_data.items():
                if confidence_dict.get(k) == None:
                    confidence_dict[k] = []
                confidence_dict[k].append(v)
                # confidence_dict[k][0:self.slice]

        return confidence_dict

    def compute_lift(self, new_conf_data, content):
        '''
        计算提升度
        :param new_conf_data: 符合置信度的项集 {"['Mix3', 'P20']": 1.0, "['Mix3', 'nexs']": 1.0}
        :param content: 获取列表的非空子集
        :return:
        '''
        # 计算提升度，需要get到support(X),support(Y),support(X交Y)
        # 定义一个列表，用于存放所有项集的集合
        dim_conf_gather = []
        for conf_i in new_conf_data:
            # 定义一个list,用于存放计算提升度的项集集合
            conf_gather = []
            conf_gather.append(conf_i[1:len(conf_i) - 1].replace("'", "").replace(", ", ",").split(","))
            conf_gather.append(
                list(set(content) - set(conf_i[1:len(conf_i) - 1].replace("'", "").replace(", ", ",").split(","))))
            conf_gather.append(content)
            dim_conf_gather.append(conf_gather)
        #         self.logger.info conf_i[1:len(conf_i)-1].replace("'","").replace(", ",",").split(",")
        self.logger.info('所有项集的集合:', dim_conf_gather)

        # 带入计算，每个项集的在用户-物品倒排表出现的次数
        # 定义一个列表用于存放data_count
        list_data_count = []
        for i in dim_conf_gather:
            data_count = self.num_count(self.dataSet, i)
            list_data_count.append(data_count)
        self.logger.info(list_data_count)

        # 计算提升度
        lift = {}
        for i in list_data_count:
            for index in range(len(i.items())):
                index_name = list(i.items())[0][0]
                if index == 0:
                    support_X = list(i.items())[0][1]
                elif index == 1:
                    support_Y = list(i.items())[1][1]
                elif index == 2:
                    support_XY = list(i.items())[2][1]

                # 根据公式计算提升度
                lift.setdefault(index_name, 0)
                lift[index_name] = (float(support_XY) / len(self.dataSet)) / (
                        (float(support_X) / len(self.dataSet)) * (float(support_Y) / len(self.dataSet)))

        for i in lift.items():
            if i[1] > 1:
                self.logger.info('由于{0}大于1，所以购买了{1}的用户，很可能会购买{2}'.format(i[1], i[0], list(set(content) - set(i[0].split("、")))))

    def run(self):
        # 第一次剪枝
        data, data_cut, data_num = self.first_cut()

        # 后面的剪枝
        data = self.later_cut(data, data_cut, data_num)

        # 计算置信度
        new_conf_data = self.compute_confidence(data)
        # self.write_files(new_conf_data)
        return new_conf_data

        # 计算提升度
        # self.compute_lift(new_conf_data, content)
