from japronto import Application

import pandas as pd
# from sklearn.externals import joblib
import joblib
from pathlib import Path
from time import strftime, localtime

dic_config = {
    'all_cols': ["dsp_id","app_id","adsolt_id","channel","city_id","os","carrier","network","device_type","adsolt_type","action_type"],  # 所有字段
    "useful_cols": ["dsp_id","app_id","adsolt_id","channel","city_id","os","carrier","network","device_type","adsolt_type","action_type"],  # 有效的特征字段,自定义
    "target_col": "click",  # 点击字段
    "xgb_model_path": "xgb_model.pkl"  # 模型路径
}

xgb_model = None

# 打印当前时间
def printTime():
    return strftime("%Y-%m-%d %H:%M:%S", localtime())

def load_model(model_path):
    global xgb_model
    print(f"[ {printTime()} ] 加载存在model:{model_path}")
    xgb_model = joblib.load(model_path)



def query_predict(request):
    try:
        json = request.json
        # print(type(json)) 
        # print("###########")
        # queryStr = json.get("queryStr")
        # print(type(queryStr))
        # print("##########")
        # print(f'请求的字符串{queryStr}')
        # queryStr = "42#31197#26465#1#107#2#1#1#1#2#0"
        # line_df = pd.DataFrame([map(int, queryStr.split("#"))], columns=dic_config['all_cols'])
        line_df = pd.DataFrame([json], columns=dic_config['all_cols'])
        predict_proba = xgb_model.predict_proba(line_df)
        rate = predict_proba[0, 1]
        print(f'===={rate}====')

    except Exception as result:
        return request.Response(text='{"status":201,"message":"%s"}' % result)
    else:
        return request.Response(text='{"status":200,"rate":%s}' % rate)


def refresh_model(request):
    try:
        json = request.json
        model_path = json.get("model_path")
        if Path(model_path).is_file():
            load_model(model_path)
        else:
            print(f"[ {printTime()} ] model_path文件不存在:{model_path}")
            raise NameError(f"[ {printTime()} ] model_path文件不存在:{model_path}")

    except Exception as result:
        return request.Response(text='{"status":201,"message":"%s"}' % result)
    else:
        return request.Response(text='{"status":"200"}')


load_model("xgb_model.pkl")


app = Application()
app.router.add_route('/query_predict', query_predict)
app.router.add_route('/refresh_model', refresh_model)
app.run(port=8082, worker_num=2)

