'''
rtb预估点击率,输入数据格式: label列,数值型特征列,需要label_encode的列
已经是label_encode好的文件
'''
import gflags
import sys

sys.path.append("..")
sys.path.append("../..")
sys.path.append("../../../..")

from evaluate.auc import AUC
import numpy as np
from utils import logs

Flags = gflags.FLAGS
gflags.DEFINE_string('log_path', '../../../../logs/xgboost_lr.log', 'log')

# 各种文件路径
gflags.DEFINE_string('in_predict_real_file', "../../../../data/deepfm_product/etl/test.label", 'onehot fit之后的内存文件,保存下来为预估用')  # 通过序列化来做
gflags.DEFINE_string('in_predict_res_file', "../../../../data/deepfm_product/predict/test_res.txt", '预估输出文件')
gflags.DEFINE_string('out_roc_curve_file', "", 'roc曲线输出')
gflags.DEFINE_string('out_ks_curve_file', "", 'ks曲线输出')
gflags.DEFINE_string('out_lift_curve_file', "", 'lift曲线输出')
gflags.DEFINE_string('out_gain_curve_file', "", 'gain曲线输出')
dic_config = {}

gflags.FLAGS(sys.argv)
logger = logs.Logger(log_path=Flags.log_path).logger

def init():
    global dic_config
    global logger
    dic_config['logger'] = logger
    dic_config['roc_curve_file_path'] = Flags.out_roc_curve_file
    dic_config['ks_curve_file_path'] = Flags.out_ks_curve_file
    dic_config['lift_curve_file_path'] = Flags.out_lift_curve_file
    dic_config['gain_curve_file_path'] = Flags.out_gain_curve_file

def run():
    y_test = np.loadtxt(Flags.in_predict_real_file, delimiter=' ')
    y_pred_test = np.loadtxt(Flags.in_predict_res_file, delimiter=' ')
    # cols_nums = y_pred_test.shape[1]
    # y_pred_test = y_pred_test[:, cols_nums-1]
    auc_entity = AUC(y_test, y_pred_test, dic_config)

    auc = auc_entity.auc_sklearn()
    print("==== test auc: %s" % auc)

    ks = auc_entity.ks_cal()
    print("==== ks: %s ===", ks)

    auc_entity.plot_roc_curve()
    auc_entity.plot_ks()

    auc_entity.plot_lift()
    auc_entity.plot_gain()

    psi = auc_entity.psi_cal()
    print("==== psi: %s ===", psi)

if __name__ == '__main__':
    init()
    run()

