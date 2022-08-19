import json

from flask import Flask, request  # flask

import pandas as pd
from sklearn.externals import joblib

dic_config = {
    'all_cols': 'dsp_id,app_id,adsolt_id,channel,city_id,os,carrier,network,device_type,adsolt_type,action_type'.split(
        ","),  # 所有字段
    "useful_cols": "dsp_id,app_id,adsolt_id,channel,city_id,os,carrier,network,device_type,adsolt_type,action_type".split(
        ","),  # 有效的特征字段,自定义
    "target_col": "click",  # 点击字段
    "xgb_model_path": "xgb_model.pkl"  # 模型路径
}

xgb_model = None


def load_model(model_path):
    global xgb_model
    print(f"加载model:{model_path}")
    xgb_model = joblib.load(model_path)


def predict(line):
    # 将行转换为df,需要对指定的非数字字段label_encode
    line_df = pd.DataFrame([line.split("#")], columns=dic_config['all_cols']).applymap(int)

    predict_proba = xgb_model.predict_proba(line_df)  # 返回一个ndarray,二维,两个概率,第一个为0的概率,第二个为1的概率

    # print(xgb_model.predict(line_df))  # 返回1/0
    rate = predict_proba[0, 1]
    # print(f'为1的概率: {rate}')  #
    return rate


app = Flask(__name__)


# @app.route("/query_predict", methods=["POST", "GET"])
# def query():
#     # 默认返回内容
#     return_request = {'code': '200', 'return_msg': '处理成功', 'result': False}
#     # 判断请求参数是否为空
#     req_data = request.get_data()
#     if req_data is None:
#         return_request['code'] = '10001'
#         return_request['return_msg'] = '请求参数为空'
#         return json.dumps(return_request, ensure_ascii=False)
#     # 传入的参数为bytes类型，需要转化成json
#     get_Data = json.loads(req_data)
#     # 操作参数
#     line = get_Data.get('queryStr')
#     result = predict(line)
#     return_request['result'] = float(result)
#     return json.dumps(return_request, ensure_ascii=False)


@app.route("/query_predict", methods=["POST", "GET"])
def query():
    # 默认返回内容
    return_request = {'code': '200', 'return_msg': '处理成功', 'result': False}
    # 判断请求参数是否为空
    # req_data = request.get_data()
    # if req_data is None:
    #     return_request['code'] = '10001'
    #     return_request['return_msg'] = '请求参数为空'
    #     return json.dumps(return_request, ensure_ascii=False)
    # 传入的参数为bytes类型，需要转化成json
    # get_Data = json.loads(req_data)
    # 操作参数
    # line = get_Data.get('queryStr')
    line = "42#31197#26465#1#107#2#1#1#1#2#0"
    result = predict(line)
    return_request['result'] = float(result)
    return json.dumps(return_request, ensure_ascii=False)


@app.route("/refresh_model", methods=["POST", "GET"])
def refresh_model():
    # 默认返回内容
    return_request = {'code': '200', 'return_msg': '处理成功'}
    # 判断请求参数是否为空
    req_data = request.get_data()
    if req_data is None:
        return_request['code'] = '10001'
        return_request['return_msg'] = '请求参数为空'
        return json.dumps(return_request, ensure_ascii=False)
    # 传入的参数为bytes类型，需要转化成json
    get_Data = json.loads(req_data)
    # 操作参数
    line = get_Data.get('model_path')
    load_model(line)
    return json.dumps(return_request, ensure_ascii=False)


load_model("xgb_model.pkl")

app.run(host='0.0.0.0', port=5000, debug=True)

