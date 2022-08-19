# -*- coding:utf-8 -*-


class ID3Tree():

    def __init__(self, dic_config={}):
        self.label = dic_config.get('label')

    # 初始化模型参数
    def load_model(self, model_path):
        import pickle
        fr = open(model_path, 'rb')
        self.model = pickle.load(fr)

    def decision(self, input_vec, node):
        print("Node: ", node.name)
        for connection, child_node in node.connections.items():
            if (connection == input_vec.get(node.name)):
                # 特征值相同
                if not child_node.connections:
                    # 根节点
                    print("predict: ", child_node.name, "; play: ", input_vec.get("play"))
                    break
                else:
                    # 非根节点，迭代
                    self.decision(input_vec, child_node)
            else:
                continue

    def predict(self, data, input_tree):
        for i in range(data.shape[0]):
            print("Index: ", i, "; vector: ", data.iloc[i])
            self.decision(data.iloc[i], input_tree.connections["Root"])
