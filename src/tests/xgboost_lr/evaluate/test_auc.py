'''
rtb预估点击率,输入数据格式: label列,数值型特征列,需要label_encode的列
已经是label_encode好的文件
'''
import os,sys

cwd = os.getcwd()
src = "/".join(cwd.split(os.sep)[:-3])
base_path = "/".join(cwd.split(os.sep)[:-4])
sys.path.append(f"{src}{os.sep}")
sys.path.append(f"{base_path}{os.sep}")


from evaluate.auc import AUC

import numpy as np

def process_demo():
    in_predict_real_file = "../../../../data/xgboost/etl/criteo_sampled_data_no_header_need_predict_real.csv"  # 真实情况
    in_predict_res_file = "../../../../data/xgboost/predict/criteo_sampled_data_no_header_need_predict_res.csv"  # 预估情况
    y_test = np.loadtxt(in_predict_real_file)
    y_pred_test = np.loadtxt(in_predict_res_file)
    auc_entity = AUC(y_test, y_pred_test)
    res = auc_entity.auc_sklearn()
    print("==== test auc: %s" % res)


if __name__ == '__main__':
    process_demo()
