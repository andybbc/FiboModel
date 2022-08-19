# -*- coding: utf-8 -*-
import requests
import json
from lxml import etree

from model.base import Base


class DFTT(Base):
    def __init__(self, page=1):
        self.send_url = "http://172.16.189.210:8666/post"
        self.dftt_url = "mini.eastday.com"
        self.dftt_pre = "edn"
        self.fmt_url = ("https://toutiao.eastday.com/toutiao_h5/RefreshJP"
                        "?htps=1&type={0}&recgid=15857996341312189"
                        "&qid=qid02650&picnewsnum=1&readhistory=&zdnews="
                        "&idx=0&pgnum={1}&os=&sclog=0&newsnum=20"
                        "&pos_pro=%E4%B8%8A%E6%B5%B7"
                        "&pos_city=%E4%B8%8A%E6%B5%B7&_=1585799676963"
                        "&jsonpcallback=Zepto1585799646113")

        # 爬虫页数
        self.page = page

        # 新闻格式（约定值）
        self.news_source = {
            "domain": self.dftt_url,
            "prefix": self.dftt_pre,
            "news": []
        }

        self.news_category = {
            "toutiao": u"推荐",
            "yule": u"娱乐",
            "jiankang": u"健康",
            "lishi": u"人文",
            "shehui": u"社会",
            "guonei": u"国内",
            "guoji": u"国际",
            "keji": u"科技",
            "qiche": u"汽车",
            "tiyu": u"体育",
            "shishang": u"时尚",
            "tupian": u"图片",
            "junshi": u"军事",
            "caijing": u"财经",
            "wzry": u"王者荣耀",
            "xingzuo": u"星座",
            "youxi": u"游戏",
            "kexue": u"科学",
            "hulianwang": u"互联网",
            "shuma": u"数码",
            "baojian": u"保健",
            "jianshen": u"健身",
            "yinshi": u"饮食",
            "jianfei": u"减肥",
            "cba": u"CBA",
            "dejia": u"德甲",
            "yijia": u"意甲",
            "wangqiu": u"网球",
            "zhongchao": u"中超",
            "xijia": u"西甲",
            "yingchao": u"英超",
            "qipai": u"棋牌",
            "gaoerfu": u"高尔夫",
            "paiqiu": u"排球",
            "yumaoqiu": u"羽毛球",
            "jiaju": u"家居",
            "waihui": u"外汇",
            "baoxian": u"保险",
            "budongchan": u"不动产",
            "huangjin": u"黄金",
            "xinsanban": u"新三板",
            "gupiao": u"股票",
            "qihuo": u"期货",
            "jijin": u"基金",
            "licai": u"理财",
            "dianying": u"电影",
            "dianshi": u"电视",
            "bagua": u"八卦"
        }

    # 爬虫 DOM 解析，获取新闻内容及插图
    def spider_content(self, url):
        r = requests.get(url)
        r.encoding = r.apparent_encoding
        dom = etree.HTML(r.text)
        d = []

        # 文本内容
        p_ele = dom.xpath('//article/div[@id="content"]/p/text()')
        # 新闻插图
        m_ele = dom.xpath(
            "//article/div[@id=\"content\"]/figure/a/img/@data-original")

        for i in range(0, len(p_ele)):
            d.append(p_ele[i])
            if i < len(m_ele):
                d.append({"url": m_ele[i]})

        return d

    def send_data(self, d):
        res = requests.post(self.send_url["SEND_URL"], data=json.dumps(d))
        if res.status_code != 200:
            print("=== send error. ", res.content)

    def gen_news(self):

        for i in range(1, self.page):
            for t, v in self.news_category.items():

                # 按分类、分页获取
                url = self.fmt_url.format(t, i)
                r = requests.get(url)
                if r.status_code != 200:
                    print("=== DFTT get news error. ", r.content)
                    continue

                # jsonp 格式解析
                ctt = json.loads(r.content[19:-1])
                data = ctt["data"]

                # 获取新闻数据
                for i in range(0, len(data)):
                    obj = data[i]

                    # 新闻组图
                    thumbnail_link = []
                    if "miniimg" in obj and len(obj["miniimg"]) > 0:
                        for i in range(0, len(obj["miniimg"])):
                            thumbnail_link.append(
                                {"url": obj["miniimg"][i]["src"]})
                    else:
                        if "lbimg" in obj and len(obj["lbimg"]) > 0:
                            for i in range(0, len(obj["lbimg"])):
                                thumbnail_link.append(
                                    {"url": obj["lbimg"][i]["src"]})

                    # 新闻详情
                    detail = self.spider_content(obj["url"])

                    d = {
                        "cat": v,
                        "title": obj["topic"],
                        "source": obj["source"],
                        "update": obj["date"] + ":00",
                        "images": thumbnail_link,
                        "raw_url": obj["url"],
                        "detail": detail
                    }

                    self.news_source["news"].append(d)
