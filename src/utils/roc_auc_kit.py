from sklearn.metrics import roc_auc_score

import numpy as np
import sys

y_test_path = sys.argv[1]
y_pred_test_path = sys.argv[2]


# 预测xgb及AUC评测

def roc_auc_score_test(y_test, y_pred_test):
    return roc_auc_score(y_test, y_pred_test)


# y_test = np.loadtxt('../../data/xgb_lr_demo_new/new_no_request_id/new_need_predict_sample_real.csv',delimiter=' ')
#
# y_pred_test = np.loadtxt('../../data/xgb_lr_demo_new/new_no_request_id/new_predict_res_sample.csv',delimiter=' ')[:, 1]

y_test = np.loadtxt(y_test_path, delimiter=' ')
y_pred_test = np.loadtxt(y_pred_test_path, delimiter=' ')[:, 1]

test_auc = roc_auc_score_test(y_test, y_pred_test)

print('test auc: %.5f' % test_auc)
