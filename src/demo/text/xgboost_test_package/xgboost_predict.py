#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import xgboost_test_package as xgb
import logging

class XgboostPredict(object):

    def __init__(self, test_weight, bst):
        self.bst = bst
        self.test_weight = test_weight

    def predict(self, output_path):
        dtest = xgb.DMatrix(self.test_weight)  # label可以不要，此处需要是为了测试效果
        logging.info('开始预测')
        preds = self.bst.predict(dtest)
        with open(output_path, 'w') as f:
            for i, pre in enumerate(preds):
                f.write(str(i + 1))
                f.write(',')
                f.write(str(int(pre) + 1))
                f.write('\n')
        logging.info('预测完成，数据写入%s文件' % output_path)

