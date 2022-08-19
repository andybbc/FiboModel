# -*- coding:utf-8 -*-
import gflags
import sys
sys.path.append("..")
from model.base import Base
from sklearn import datasets
from sklearn.preprocessing import normalize
from sklearn.model_selection import train_test_split
from predict.logistic_regression import LogisticRegression as LRPredict
from model.logistic_regression import LogisticRegression as LRModel
from utils import logs


Flags = gflags.FLAGS
gflags.DEFINE_string('store_path', '../../data/demo/lr/lr_model.txt', '模型参数存储路径')
gflags.DEFINE_string("log_path", '../../log/log', '日志输出路径')

dic_config = {
    'alpha': 0.1,
    'n_iter': 3000
}

# 生成训练、校验使用数据
def data_generate():
    # 加载鸢尾花数据集
    data = datasets.load_iris()

    # 鸢尾花数据集有三种分类结果，这里去除 0 分类，生成逻辑分类（0 | 1）数据集
    # normalize？
    X = normalize(data.data[data.target != 0])
    y = data.target[data.target != 0]
    y[y == 1] = 0
    y[y == 2] = 1

    # 按比例拆分
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=2)

    return X_train, y_train, X_test, y_test


def train(store_path):
    # 加载数据集
    X_train, y_train, X_test, y_test = data_generate()

    # 加载模型
    model = LRModel(dic_config)

    # 训练
    model.fit(X_train, y_train)

    # 计算准确率
    accuracy = model.score(X_test, y_test)
    print("accuracy：", accuracy)

    # AUC 算法一计算准确率
    accuracy1 = model.score1(X_test, y_test)
    print("accuracy1：", accuracy1)

    # AUC 算法二计算准确率
    accuracy2 = model.score2(X_test, y_test)
    print("accuracy2：", accuracy2)

    # 存储模型
    model.storeModel(store_path)


def predict(store_path):
    # 加载模型
    model = LRPredict(dic_config)
    model.loadModel(store_path)
    if not hasattr(model, "_w"):
        return

    # 创建预测实例（单一实例）
    X_train, y_train, X_test, y_test = data_generate()
    X_test_data = X_test[0]

    y_pred = model.predict(X_test_data)
    print(y_pred)


if __name__ == '__main__':
    gflags.FLAGS(sys.argv)
    dic_config['logger'] = logs.Logger(log_path=Flags.log_path).logger
    store_path = Flags.store_path
    train(store_path)
    predict(store_path)
