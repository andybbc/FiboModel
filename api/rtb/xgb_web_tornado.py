import json

import pandas as pd
from sklearn.externals import joblib

import tornado.ioloop
import tornado.web
from tornado.escape import json_decode
from tornado.options import define, options

define("port", default=8888, help='run a test')

dic_config = {
    'all_cols': ["dsp_id", "app_id", "adsolt_id", "channel", "city_id", "os", "carrier", "network", "device_type",
                 "adsolt_type", "action_type"],  # 所有字段
    "useful_cols": ["dsp_id", "app_id", "adsolt_id", "channel", "city_id", "os", "carrier", "network", "device_type",
                    "adsolt_type", "action_type"],  # 有效的特征字段,自定义
    "target_col": "click",  # 点击字段
    "xgb_model_path": "xgb_model.pkl"  # 模型路径
}

xgb_model = None


def load_model(model_path):
    global xgb_model
    print(f"加载model:{model_path}")
    xgb_model = joblib.load(model_path)


load_model("xgb_model.pkl")


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        info = {'user': 'leno'}
        jinfo = json.dumps(info)
        self.write(jinfo)

    def post(self, *args, **kwargs):
        print('post message')
        print(self.request.remote_ip)
        print(self.request.body_arguments)
        data = json_decode(self.request.body)
        user = data['user']
        pw = data['passwd']
        print(user, pw)
        jdata = json.dumps(data)
        print(jdata)
        self.write(jdata)

    def set_default_headers(self):
        self.set_header('Content-type', 'application/json;charset=utf-8')


class QueryPredict(tornado.web.RequestHandler):  # 注意继承RequestHandler 而不是redirectHandler
    def post(self, *args, **kwargs):
        # data = json_decode(self.request.body)
        # queryStr = data['queryStr']
        queryStr = "42#31197#26465#1#107#2#1#1#1#2#0"
        line_df = pd.DataFrame([queryStr.split("#")], columns=dic_config['all_cols']).applymap(int)
        predict_proba = xgb_model.predict_proba(line_df)
        rate = predict_proba[0, 1]
        self.write(json.dumps({'res': float(rate)}))


class RefreshModel(tornado.web.RequestHandler):
    def post(self, *args, **kwargs):
        data = json_decode(self.request.body)
        model_path = data['model_path']
        load_model(model_path)
        self.write(json.dumps({'res': "ok"}))


application = tornado.web.Application([
    (r'/', MainHandler),
    (r'/query_predict/', QueryPredict),  # 路由
    (r'/refresh_model/', RefreshModel)
])

if __name__ == '__main__':
    application.listen(options.port)  # 创建1个socket对象
    tornado.ioloop.IOLoop.instance().start()  # conn,addr=socket.accept()进入监听状态
