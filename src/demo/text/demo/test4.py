"""
特征重要性排序，特征重要性选择

未理解，未跑通
https://blog.csdn.net/waitingzby/article/details/81610495
2019年6月15日，跑通了，但是出现很多warning
"""
# plot feature importance manually
from numpy import loadtxt
from xgboost_test_package import XGBClassifier
from xgboost_test_package import plot_importance
from matplotlib import pyplot
import numpy as np
# load data
#dataset = loadtxt('pima-indians-diabetes.csv', delimiter=",")
# split data into X and y


# use feature importance for feature selection
from numpy import loadtxt
from numpy import sort
from xgboost_test_package import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.feature_selection import SelectFromModel

n_group = 2
n_choice = 3
X = np.random.uniform(0, 100, [n_group * n_choice, 6])
y = np.array([np.random.choice([0, 1, 2], 3, False) for i in range(n_group)]).flatten()

# split data into train and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=6)
# fit model on all training data
model = XGBClassifier()
model.fit(X_train, y_train)
# make predictions for test data and evaluate
y_pred = model.predict(X_test)
predictions = [round(value) for value in y_pred]
accuracy = accuracy_score(y_test, predictions)
print("Accuracy: %.2f%%" % (accuracy * 100.0))
# Fit model using each importance as a threshold
thresholds = sort(model.feature_importances_)

for thresh in thresholds:
    # select features using threshold
    selection = SelectFromModel(model, threshold=thresh, prefit=True)
    select_X_train = selection.transform(X_train)
    # train model
    selection_model = XGBClassifier()
    selection_model.fit(select_X_train, y_train)
    # eval model
    select_X_test = selection.transform(X_test)
    y_pred = selection_model.predict(select_X_test)
    predictions = [round(value) for value in y_pred]
    accuracy = accuracy_score(y_test, predictions)
    print("Thresh=%.3f, n=%d, Accuracy: %.2f%%" % (thresh, select_X_train.shape[1], accuracy*100.0))
