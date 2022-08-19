import pickle

import sklearn
from japronto import Application

import pandas as pd
import joblib
from pathlib import Path
from time import strftime, localtime
import numpy as np

from deepctr.layers import custom_objects
from keras.models import load_model

dic_config = {
    "use_model_type": "deepfm",  # deepfm / xdeepfm
    "need_label_encode_cols_num": 26,
    "select_cols": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
                    21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39],  # 要包含0列
    "dense_feature_type": "log"  # 数值型的字段处理方式,需要加载ms
}

# 预测用
pred_columns = list(str(i) for i in range(1, len(dic_config['select_cols'])))

# 数值型的字段的长度
dense_cols_num = len(dic_config["select_cols"]) - dic_config['need_label_encode_cols_num'] - 1

#

deepfm_model = None
label_dict = None
mms = None


# 打印当前时间
def printTime():
    return strftime("%Y-%m-%d %H:%M:%S", localtime())


def load_deepfm_model(deepfm_model_path):
    global deepfm_model
    deepfm_model = load_model(deepfm_model_path, custom_objects)


def load_mms_save_file(mms_save_file):
    '''
    dense feature 的minmaxscaler处理
    :param mms_save_file:
    :return:
    '''
    global mms
    mms = joblib.load(mms_save_file)


def load_label_encode(label_encode_path):
    global label_dict
    print(f"[ {printTime()} ] 加载label_encode:{label_encode_path}")
    with open(label_encode_path, 'rb') as f:
        label_dict = pickle.load(f)  # 是一个dict,字段映射


def query_predict(request):
    global label_dict
    try:
        input_list = request.json
        # print(f"请求的json:{input_list}")
        if dic_config['need_label_encode_cols_num'] > 0:
            for index, label_encoder in label_dict.items():
                need_encode_data = input_list[index]
                if need_encode_data not in label_encoder.classes_:
                    label_dict[index].classes_ = np.append(label_encoder.classes_, 'Unknown')
                    input_list[index] = int(label_encoder.transform(['Unknown'])[0])
                else:
                    input_list[index] = int(label_encoder.transform([input_list[index]])[0])

        if dic_config['dense_feature_type'] == "minmaxscaler":
            ndarray1 = np.array([input_list[:dense_cols_num]])  # 找到数字列
            df_mms = mms.transform(ndarray1)
            pd_stg_input = pd.concat([pd.DataFrame(df_mms), pd.DataFrame(
                [input_list[dense_cols_num: -1]]
            )], axis=1)

        else:
            for i in range(0, dense_cols_num):
                if input_list[i] > -1:
                    input_list[i] = np.log(input_list[i] + 1)
                else:
                    input_list[i] = -1

            pd_stg_input = pd.DataFrame([input_list])

        # print(f"转化后的df:{pd_stg_input.values}")

        # return
        # 上面准备完成后开始预测前
        pd_stg_input.columns = pred_columns
        # print(f"columns:{pd_stg_input.columns}")
        test_model_input = {name: pd_stg_input[name] for name in pd_stg_input.columns}
        # print(f"test_model_input:{test_model_input}")
        print(f"deepfm_model{deepfm_model}")

        rate = deepfm_model.predict(test_model_input)
        # print(f"rate:{rate}")
    except Exception as result:
        print(result)
        return request.Response(text='{"status":201,"message":"%s"}' % result)
    else:
        return request.Response(text='{"status":200,"rate":%s}' % rate)


def refresh_model(request):
    # print("=" * 10)
    try:
        json = request.json
        model_path = json.get("model_path")
        label_encode_path = json.get("label_encode_path")
        mms_save_file_path = json.get("mms_save_file")

        if dic_config['need_label_encode_cols_num'] > 0:
            # 如果需要
            load_label_encode(label_encode_path)

        if dic_config['dense_feature_type'] == "minmaxscaler":
            load_mms_save_file(mms_save_file_path)

        # 肯定需要加载的
        if Path(model_path).is_file():
            load_model(model_path)
        else:
            print(f"[ {printTime()} ] model_path文件不存在:{model_path}")
            raise NameError(f"[ {printTime()} ] model_path文件不存在:{model_path}")

    except Exception as result:
        return request.Response(text='{"status":201,"message":"%s"}' % result)
    else:
        return request.Response(text='{"status":"200"}')


if __name__ == '__main__':
    # 初始化,肯定要加载这个
    load_deepfm_model("deepfm_model.h5")

    if dic_config['need_label_encode_cols_num'] > 0:
        load_label_encode("label.out")

    if dic_config['dense_feature_type'] == "minmaxscaler":
        load_mms_save_file("mms.save")

    app = Application()
    app.router.add_route('/query_predict', query_predict)
    app.router.add_route('/refresh_model', refresh_model)
    app.run(port=8084, worker_num=1)

