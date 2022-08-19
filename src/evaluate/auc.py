"""
#解释一
auc = sum(I(P(+) ,  P(-))) / M(+)*N(-)
if P(正样本) > P(负样本) I(P(正样本), P(负样本)) = 1
if P(正样本) = P(负样本) I(P(正样本), P(负样本)) = 0.5
if P(正样本) < P(负样本) I(P(正样本), P(负样本)) = 0
#解释二
auc = sum( index_i \in posiitveclass Rank_index_i) - M*(M+1)/2     / M*N
"""
import sys
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score, recall_score, precision_score, f1_score, accuracy_score, roc_curve, auc, confusion_matrix
from matplotlib import pyplot as plt

class AUC():
    '''
    AUC评价算法类
        AUC可理解为：随机抽出一对样本（一个正样本，一个负样本），然后用训练得到的分类器来对这两个样本进行预测，
    预测得到正样本的概率大于负样本概率的概率
    '''

    def __init__(self, labels, preds, dic_config={}):
        self.labels = labels  # 正负样本集
        self.preds = preds  # 样本集预测值
        self.n_bins = dic_config.get('n_bins', 100)  # 矩阵长度
        self.roc_curve_file_path = dic_config.get('roc_curve_file_path')  # ROC曲线
        self.ks_curve_file_path = dic_config.get('ks_curve_file_path')  # KS曲线
        self.lift_curve_file_path = dic_config.get('lift_curve_file_path')  # 提升图 lift曲线
        self.gain_curve_file_path = dic_config.get('gain_curve_file_path')  # 增益图 gain曲线
    def calculate1(self):
        '''
        计算方法一：在有M个正样本,N个负样本的数据集里。一共有M*N对样本（一对样本即，一个正样本与一个负样本）。
        统计这 M*N 对样本里，正样本的预测概率大于负样本的预测概率的个数。
        '''
        # 正负样本集个数
        postive_len = sum(self.labels)
        negative_len = len(self.labels) - postive_len
        # 正负样本组合个数
        total_case = postive_len * negative_len

        # 设置两个稀疏矩阵记录正样本预测概率大于负样本预测概率的个数
        pos_histogram = [0 for _ in range(self.n_bins)]
        neg_histogram = [0 for _ in range(self.n_bins)]

        # 将概率值映射至正负样本的稀疏矩阵
        bin_width = 1.0 / self.n_bins

        for i in range(len(self.labels)):
            nth_bin = int(self.preds[i] / bin_width)
            if self.labels[i] == 1:
                pos_histogram[nth_bin] += 1
            else:
                neg_histogram[nth_bin] += 1

        accumulated_neg = 0
        satisfied_pair = 0
        for i in range(self.n_bins):
            satisfied_pair += (pos_histogram[i] * accumulated_neg +
                               pos_histogram[i] * neg_histogram[i] * 0.5)
            accumulated_neg += neg_histogram[i]

        return satisfied_pair / float(total_case)

    # def calculate2(self):
    #     '''
    #     计算方法二：所有的正负样本对中，正样本排在负样本前面占样本对数的比例，即这个概率值。
    #     '''
    #     f = list(zip(self.preds, self.labels))
    #     # 按概率大小排序；rank 为概率排序后的数组
    #     rank = [values2 for values1, values2 in sorted(f, key=lambda x: x[0])]
    #
    #     # 取出正样本集(index 从 0 开始，故 i+1)
    #     rankList = [i + 1 for i in range(len(rank)) if rank[i] == 1]
    #
    #     # 正负样本集个数
    #     posNum = 0
    #     negNum = 0
    #     for i in range(len(self.labels)):
    #         if self.labels[i] == 1:
    #             posNum += 1
    #         else:
    #             negNum += 1
    #
    #     auc = 0
    #     auc = (sum(rankList) - (posNum * (posNum + 1)) / 2) / (posNum * negNum)
    #     return auc

    def auc(self):
        """
        fp-tp curve
        self.labels is true labels
        self.preds is probability
        """
        # positve samples
        pos = [j for i, j in zip(self.labels, self.preds) if i == 1]
        # negative samples
        neg = [j for i, j in zip(self.labels, self.preds) if i == 0]

        nominator = 0.0
        for i in pos:
            for j in neg:
                if i > j:
                    nominator += 1
                elif i == j:
                    nominator += 0.5
                else:
                    nominator += 0
        M = len(pos)
        N = len(neg)
        # print(nominator, M, N)
        auc_ = nominator / (M * N)

        return auc_

    def auc_sort(self):
        """
        fp-tp curve
        self.labels is true labels
        self.preds is probability
        self.preds 0,1 0,2 0,3 0,4 0,5  排序
        self.labels     0    1   0   0   1
        """
        pos_len = sum(self.labels)
        neg_len = len(self.labels) - pos_len
        total_case = pos_len * neg_len

        labels_pred = zip(self.labels, self.preds)
        # 先对y_hat从小到大排序 如果y_hat相等对y从小到大排序
        labels_pred = sorted(labels_pred, key=lambda x: (x[1], x[0]))
        print(f"labels_pred {labels_pred}")
        accumulated_neg = 0
        satisfied_pair = 0
        # 这种算法是有问题的因为当预测概率相同的时候应该乘于 0.5
        prev = -1
        prev_num = 0
        for i in range(len(self.labels)):
            if labels_pred[i][0] == 1:
                if prev == labels_pred[i][1]:
                    print("ok")
                    satisfied_pair -= prev_num * 0.5
                satisfied_pair += accumulated_neg
            else:
                if labels_pred[i][1] != prev:
                    prev = labels_pred[i][1]
                    prev_num = 1
                else:
                    prev_num += 1
                accumulated_neg += 1

        return satisfied_pair / float(total_case)

    def auc_bin(self):
        """
        对正负样本的预测值分别分桶 构建直方图再计算满足条件的正负样本对
        fp-tp curve
        self.labels is true labels
        self.preds is probability
        """
        pos_len = sum(self.labels)
        neg_len = len(self.labels) - pos_len
        total_case = pos_len * neg_len
        pos_histogram = [0 for _ in range(self.n_bins + 1)]
        neg_histogram = [0 for _ in range(self.n_bins + 1)]
        bin_width = 1.0 / self.n_bins
        # 分桶相当于对预测值进行排序，统计预测值第i大的样本的个数
        for i in range(len(self.labels)):
            nth_bin = int(self.preds[i] / bin_width)  # [0 , bins - 1]
            # print(f"nth_bin {nth_bin} ")
            if self.labels[i] == 1:
                pos_histogram[nth_bin] += 1
            else:
                neg_histogram[nth_bin] += 1
        accumulated_neg = 0
        satisfied_pair = 0
        for i in range(self.n_bins):
            satisfied_pair += (pos_histogram[i] * accumulated_neg + pos_histogram[i] * neg_histogram[i] * 0.5)
            """
            对上面的理解 pos_histogram[i] 表示第i+1大的预测值所在的桶中样本的个数
            accumulated_neg 表示预测值小于第i+1大的预测值的负样本总个数，所以这个公式代表 P(正样本) > P(负样本)
            第二个公式很好理解 表示 P(正样本) == P(负样本)
            P(正样本) < P(负样本) 时为0不需要写出来
            """
            accumulated_neg += neg_histogram[i]
        return satisfied_pair / float(total_case)

    def auc_sklearn(self):
        return roc_auc_score(self.labels, self.preds)

    def plot_confusion_matrix(y, y_hat, labels=[1, 0]):
        # y是真实的标签，y_hat是预测的标签，labels表示label的展示顺序
        cm = confusion_matrix(y, y_hat, labels=labels)
        plt.figure(figsize=(5, 5))
        plt.imshow(cm, interpolation='nearest', cmap=plt.cm.binary)
        plt.xticks(np.array(range(len(labels))), labels, rotation=90)  # 将标签印在x轴坐标上
        plt.yticks(np.array(range(len(labels))), labels)  # 将标签印在y轴坐标上

        plt.title('Confusion Matrix')  # 标题
        plt.xlabel('predict label')  # x轴
        plt.ylabel('true label')  # y轴

        ind_array = np.arange(len(labels))
        x, y = np.meshgrid(ind_array, ind_array)

        for x_val, y_val in zip(x.flatten(), y.flatten()):
            c = cm[y_val][x_val]
            plt.text(x_val, y_val, "%s" % (c,), color='red', fontsize=20, va='center', ha='center')

        plt.show()

    def plot_roc_curve(self, pos_label=1):
        # This is a function to plot a roc curve
        # y指的是真实值，y_hat_proba指的是预测的概率结果
        y = self.labels
        y_hat_proba = self.preds

        fpr, tpr, thresholds = roc_curve(y, y_hat_proba, pos_label=pos_label)
        AUC = auc(fpr, tpr)
        lw = 2
        plt.figure(figsize=(8, 8))
        plt.plot(fpr, tpr, color='darkorange',
                 lw=lw, label='ROC curve (area = %0.4f)' % AUC)  ###假正率为横坐标，真正率为纵坐标做曲线
        plt.plot([0, 1], [0, 1], color='navy', lw=lw, linestyle='--')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('ROC Curve')
        plt.legend(loc="lower right")
        # plt.show()
        plt.savefig(self.roc_curve_file_path, dpi=1000)

    def ks_cal(self):
        # 计算ks值
        fpr, tpr, _ = roc_curve(self.labels, self.preds)
        diff = np.subtract(tpr, fpr)
        ks = diff.max()
        return ks

    def plot_ks(self):
        # 画ks曲线
        y = self.labels
        y_hat_proba = self.preds

        fpr, tpr, thresholds = roc_curve(y, y_hat_proba)
        diff = np.subtract(tpr, fpr)
        ks = diff.max()

        y_len = len(y)

        # 计算比例，这样计算比较快
        # 也可以自己划分样本的比例，自己计算fpr，tpr
        y_hat_proba_sort = sorted(y_hat_proba, reverse=True)
        cnt_list = []
        cnt = 0
        for t in thresholds:
            for p in y_hat_proba_sort[cnt:]:
                if p >= t:
                    cnt += 1
                else:
                    cnt_list.append(cnt)
                    break
        percentage = [c / float(y_len) for c in cnt_list]

        if min(thresholds) <= min(y_hat_proba_sort):
            percentage.append(1)

        # 以下为画图部分
        best_thresholds = thresholds[np.argmax(diff)]
        best_percentage = percentage[np.argmax(diff)]
        best_fpr = fpr[np.argmax(diff)]

        lw = 2
        plt.figure(figsize=(8, 8))
        plt.plot(percentage, tpr, color='darkorange',
                 lw=lw, label='True Positive Rate')
        plt.plot(percentage, fpr, color='darkblue',
                 lw=lw, label='False Positive Rate')
        plt.plot(percentage, diff, color='darkgreen',
                 lw=lw, label='diff')
        plt.plot([best_percentage, best_percentage], [best_fpr, best_fpr + ks],
                 color='navy', lw=lw, linestyle='--', label='ks = %.2f, thresholds = %.2f' % (ks, best_thresholds))

        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('percentage')
        plt.title('KS Curve')
        plt.legend(loc="lower right")
        # plt.show()
        plt.savefig(self.ks_curve_file_path, dpi=1000)

    def plot_lift(self, bins=10):
        y = self.labels
        y_hat_proba = self.preds

        if type(y) == pd.core.frame.DataFrame:
            y = y.iloc[:, 0]

        lift_list = []

        total_count = len(y)
        pos_count = int(np.sum(y))
        pos_proportion = pos_count / float(total_count)

        df = pd.DataFrame({'y': y, 'y_hat_proba': y_hat_proba})
        df.sort_values(by='y_hat_proba', inplace=True, ascending=False)
        df.reset_index(drop=True, inplace=True)

        binlen = len(y) / bins
        cuts = [int(i * binlen) for i in range(1, bins)]
        cuts.append(total_count)
        x = [float(i) / bins for i in range(1, bins + 1)]

        for c in cuts:
            y_hat = list(np.repeat(1, c)) + list(np.repeat(0, total_count - c))
            lift_list.append(precision_score(df['y'], y_hat) / pos_proportion)

        lw = 2
        plt.figure(figsize=(8, 8))
        plt.plot(x, lift_list, color='darkorange', lw=lw, label='model lift')
        plt.plot([x[0], x[-1]], [1, 1], color='darkblue', lw=lw, label='random lift', linestyle='--')

        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, lift_list[0] + 1])
        plt.xlabel('The proportion of datasets')
        plt.title('Lift Curve')
        plt.legend(loc="lower right")
        plt.grid()
        # plt.show()
        plt.savefig(self.lift_curve_file_path, dpi=1000)

    def plot_gain(self, bins=10):
        y = self.labels
        y_hat_proba = self.preds

        if type(y) == pd.core.frame.DataFrame:
            y = y.iloc[:, 0]

        gain_list = []

        total_count = len(y)
        pos_count = int(np.sum(y))

        df = pd.DataFrame({'y': y, 'y_hat_proba': y_hat_proba})
        df.sort_values(by='y_hat_proba', inplace=True, ascending=False)
        df.reset_index(drop=True, inplace=True)

        binlen = len(y) / bins
        cuts = [int(i * binlen) for i in range(1, bins)]
        cuts.append(total_count)
        x = [0] + [float(i) / bins for i in range(1, bins + 1)]

        for c in cuts:
            cumulative_pos = np.sum(df['y'][:c])
            gain_list.append(cumulative_pos / float(pos_count))
        gain_list = [0] + gain_list

        lw = 2
        plt.figure(figsize=(8, 8))
        plt.plot(x, gain_list, color='darkorange', lw=lw, label='proportion of cumulative events(model)')
        plt.plot([0, 1], [0, 1], color='darkblue', lw=lw, label='proportion of cumulative events(random)',
                 linestyle='--')

        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('The proportion of datasets')
        plt.title('Gain Curve')
        plt.legend(loc="lower right")
        plt.grid()
        # plt.show()
        plt.savefig(self.gain_curve_file_path, dpi=1000)

    def psi_cal(self, bins=10):
        score_actual = self.labels
        score_except = self.preds

        actual_min = score_actual.min()
        actual_max = score_actual.max()

        binlen = (actual_max - actual_min) / bins
        cuts = [actual_min + i * binlen for i in range(1, bins)]
        cuts.insert(0, -float("inf"))
        cuts.append(float("inf"))

        actual_cuts = np.histogram(score_actual, bins=cuts)
        except_cuts = np.histogram(score_except, bins=cuts)

        actual_df = pd.DataFrame(actual_cuts[0], columns=['actual'])
        predict_df = pd.DataFrame(except_cuts[0], columns=['predict'])
        psi_df = pd.merge(actual_df, predict_df, right_index=True, left_index=True)

        psi_df['actual_rate'] = (psi_df['actual'] + 1) / psi_df['actual'].sum()  # 计算占比，分子加1，防止计算PSI时分子分母为0
        psi_df['predict_rate'] = (psi_df['predict'] + 1) / psi_df['predict'].sum()

        psi_df['psi'] = (psi_df['actual_rate'] - psi_df['predict_rate']) * np.log(
            psi_df['actual_rate'] / psi_df['predict_rate'])

        psi = psi_df['psi'].sum()

        return psi
