#!/usr/bin/env python
# -*- coding: utf-8 -*-

if __name__ =='__main__':
    from xgboost_train import XgboostTrain
    from xgboost_predict import XgboostPredict
    import logging

    logging.basicConfig(level=logging.INFO, filename='/home/xiaoxinwei/log/xboost.log')
    xgtrain = XgboostTrain('/home/xiaoxinwei/data/xgboost/training.csv', '/home/xiaoxinwei/data/xgboost/testing.csv', class_number=11)
    xgtrain.load_data()
    test_weight, model = xgtrain.train()

    xgpredict = XgboostPredict(test_weight, model)
    xgpredict.predict('output_xgboost.csv')