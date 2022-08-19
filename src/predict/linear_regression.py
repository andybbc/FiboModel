# -*- coding:utf-8 -*-


class LinearRegression():
    '''
    线性回归类
    参数：
        alpha: 迭代步长
        n_iter:迭代次数
    使用示例：
        lr = LinearRegression()          # 实例化类
        lr.initialPara(w_start, b_start) # 初始化预估参数
        lr.fit(X_train,y_train)          # 训练模型
        y_predict = lr.predict(X_test)   # 预测训练数据
        lr.plotFigure()                  # 用于画出样本散点图与预测模型
    '''
    def __init__(self, dic_config={}):
        pass

    # 初始化模型参数
    def load_model(self, filename):
        import pickle
        with open(filename, 'rb') as file:
            self.model = pickle.load(file)

    def predict(self, X, w, b):
        return w * X + b