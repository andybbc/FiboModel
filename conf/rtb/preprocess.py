# xgb.XGBClassifier参数

CONFIG = {
    'common': {
        'dev': True,  # 调参模式，需不需要拆分成Train,vali,Test,auc判断
        'file_separator': '#',

        # 国内ctr、cvr
        # 'need_label_encode_cols_num': 17,  # baidu
        # 'need_label_encode_cols_num': 17,  # baidu cvr
        'need_label_encode_cols_num': 20,  # oppo

        # "select_cols": [0, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 24, 25, 29, 30, 36, 37, 45, 46, 50, 51, 57, 58, 61], # baidu
        # "select_cols": [4, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 29, 30, 31, 32, 33, 37, 38, 44, 45, 53, 54, 58, 59, 65, 66, 69], # baidu cvr

        # oppo
        "select_cols": [0, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 32, 33, 34,
                        35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69],



        # 海外ctr
        # 'need_label_encode_cols_num': 25,

        # "select_cols": [0, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37,
        #                 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65],


        # "dense_feature_type": "minmaxscaler"  # minmaxscaler / log /none , 数值部分字段的处理方式
        "dense_feature_type": "none"
    },

    'rbt': {
        'dev': False,  # 调参模式，需不需要拆分成Train,vali,Test,auc判断
        'file_separator': ',',
        'need_label_encode_cols_num': 26,  # 需要转换字段的数目
        "select_cols": [0, 1, 2, 3, 4, 5, 6, 11, 12, 13],
        "if_minmaxscaler": True  # 数值型的列是否做归一化
    },
    'criteo': {
        'dev': False,  # 调参模式，需不需要拆分成Train,vali,Test,auc判断
        'file_separator': ',',
        'need_label_encode_cols_num': 26,  # 需要转换字段的数目
        "select_cols": [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,
                        21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39],  # 训练的字段,0为label,如果为待预测文件,这个不变,只是文件第一列少了
        "dense_feature_type": "none"  # minmaxscaler / log /none , 数值部分字段的处理方式
    },
    'xgboost': {
        'dev': False,  # 调参模式，需不需要拆分成Train,vali,Test,auc判断
        'file_separator': '#',
        'need_label_encode_cols_num': 11,  # 需要转换字段的数目
        "select_cols": [0, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
        "dense_feature_type": "none"  # minmaxscaler / log /none , 数值部分字段的处理方式
    },
}
