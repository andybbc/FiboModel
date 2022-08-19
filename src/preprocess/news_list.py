# coding:utf-8
import sys
sys.path.append("../..")
sys.path.append("..")

from PIL import Image
from io import StringIO
import requests
import hashlib
import string
import random
import shutil
import time
import json
import os
from model.keyword_extract import KWExtract
from utils.duplicate_kit import DuplicateKit
from utils.redis_kit import RedisKit
from utils.mongo_kit import MongoKit
from utils.oss_kit import OSSKit
from conf.reco.category import CategoryMap


class NewsList:
    def __init__(self, raw_news_list, newsid_prefix=''):
        self.newsid_prefix = newsid_prefix
        # 新闻列表
        self.news_list = raw_news_list
        # mongodb
        self.mongo_client = MongoKit(self.newsid_prefix)
        # redis
        self.redis_client = RedisKit(self.newsid_prefix)
        # oss
        self.OSSKit = OSSKit()

        # 图片下载路径
        self.date_dir_name = time.strftime(
            '%Y%m%d', time.localtime(time.time()))
        localtime = time.strftime(
            '%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))
        randstr = ''.join(random.sample(string.ascii_letters, 4))
        image_download_dir = './tmp/' + localtime + randstr
        if not os.path.exists(image_download_dir):
            os.makedirs(image_download_dir)
        self.image_download_dir = image_download_dir

        # cdn
        self.cdn_host = 'http://cdn.cashslide.cn/'

    def gen_newsid(self):
        # 0. 生成新闻id
        for news in self.news_list:
            if 'id' not in news:
                name_str = news['title'].encode(encoding='UTF-8')
                news['id'] = hashlib.md5(name_str).hexdigest()

            news['id'] = self.newsid_prefix + '_' + news['id']

    def filter_no_images_news(self):
        # 0.5 过滤异常新闻

        # 中投不过滤
        if self.newsid_prefix == 'chn':
            return

        valid_news_list = []
        for news in self.news_list:
            is_valid = True

            # 过滤没有缩略图的新闻
            if not news['images']:
                is_valid = False

            # 过滤时间错误的
            if len(news['update']) != 19:
                is_valid = False

            if 'detail' not in news or not news['detail']:
                is_valid = False

            # 有黑名单关键词的
            if news['title'].find('郝海东') != -1:
                is_valid = False
            for line in news['detail']:
                if type(line) == str:
                    if line.find('郝海东') != -1:
                        is_valid = False

            if is_valid:
                valid_news_list.append(news)

        self.news_list = valid_news_list

    def filter_uploaded_news(self):
        # 0.5 过滤已经上传过的新闻id
        valid_news_list = []
        for news in self.news_list:
            if not self.redis_client.is_news_uploaded(news['id']):
                valid_news_list.append(news)

        for news in valid_news_list:
            # 存入redis已上传的
            self.redis_client.save_uploaded_newsid(news['id'])
        self.news_list = valid_news_list

    def gen_tags(self):
        wk_extract = KWExtract()
        # 1. 生成标签
        for news in self.news_list:
            # 标题标签提取
            title_tags_dict = wk_extract.extract_tags(news['title'], topK=3)
            title_tags = list(title_tags_dict.keys())
            news['tags_weight'] = title_tags_dict
            news['tags'] = title_tags

            # 正文标签提取
            detail_text = []
            for line in news['detail']:
                if type(line) == 'str':
                    detail_text.append(line)
            detail_text = '\n'.join(detail_text)
            detail_tags_dict = wk_extract.extract_tags(news['title'], topK=20)
            detail_tags = list(detail_tags_dict.keys())
            news['detail_tags'] = detail_tags

            # 合并
            news['all_tags_weight'] = {**detail_tags_dict, **title_tags_dict}
            news['all_tags'] = list(set(title_tags + detail_tags))

    def remove_duplicate(self):
        # 2. 新闻去重
        # 2.1. 本列表内部去重
        dkit = DuplicateKit()
        self.news_list = dkit.remove_internal_duplicate(self.news_list)

        # 2.2. 和历史新闻去重
        # history_list = self.mongo_client.get_old_news(86400*2)
        # self.news_list = dkit.remove_history_duplicate(self.news_list, history_list)
        print('after DuplicateKit count:', len(self.news_list))

    def insert_image(self, img_type, img_url, news_id):
        self.need_down_image_list[img_url] = {
            'news_id': news_id,
            'md5': hashlib.md5(img_url.encode(encoding='UTF-8')).hexdigest(),
            'img_type': img_type,
            # 'format'
            # 'down_status'
        }
        img_uri = img_url.split('/')[-1]
        s_img_uri = img_uri.split('.')
        # 如果有文件格式
        if len(s_img_uri) >= 2:
            img_format = s_img_uri[-1]
            self.need_down_image_list[img_url]['format'] = img_format

    def download_image(self):
        # 3. 下载图片
        self.need_down_image_list = {}
        # 取出图片
        for news in self.news_list:
            for v in news['images']:
                # 缩略图
                self.insert_image('thumbnail', v['url'], news['id'])
            for line in news['detail']:
                # 正文图片
                if type(line) == dict:
                    self.insert_image('detail', line['url'], news['id'])
        # 下载
        for img_url in self.need_down_image_list:
            img_info = self.need_down_image_list[img_url]
            try:
                res = requests.get(img_url, timeout=5)
                if res.status_code == 200:
                    img_info['down_status'] = True
                    # 文件格式
                    if 'format' in img_info:
                        img_format = img_info['format']
                    else:
                        image = Image.open(StringIO.StringIO(res.content))
                        img_format = image.format.lower()
                        img_info['format'] = img_format
                    # 保存文件
                    img_url_md5 = img_info['md5']
                    file_name = '%s/%s.%s' % (
                        self.image_download_dir, img_url_md5, img_format)
                    with open(file_name, 'wb') as f:
                        f.write(res.content)
                    img_info['local_file'] = file_name
                    # 图片文件的md5
                    img_info['file_md5'] = self.cal_file_md5(file_name)
                else:
                    print("=== failed to get images, ", res.content)
                    img_info['down_status'] = False
            except:
                print("=== failed to get images: exception ")
                img_info['down_status'] = False

    def cal_file_md5(self, filename):
        if not os.path.isfile(filename):
            return
        with open(filename, 'rb') as f:
            data = f.read()
            file_md5 = hashlib.md5(data).hexdigest()
        return file_md5

    def filter_invalid(self):
        # 4. 过滤失效图片新闻
        # 下载失败的
        invalid_newsid_list = set([])
        for img_url in self.need_down_image_list:
            img_info = self.need_down_image_list[img_url]
            if not img_info['down_status']:
                invalid_newsid_list.add(img_info['news_id'])

        # 缩略图重复的
        news_thumbnail_dict = {}
        for img_url in self.need_down_image_list:
            img_info = self.need_down_image_list[img_url]
            if not img_info['down_status']:
                continue
            if img_info['img_type'] == 'thumbnail':
                if img_info['news_id'] not in news_thumbnail_dict:
                    news_id = img_info['news_id']
                    news_thumbnail_dict[news_id] = []
                news_thumbnail_dict[news_id].append(img_info['file_md5'])

        for news_id in news_thumbnail_dict:
            list_len = len(news_thumbnail_dict[news_id])
            set_len = len(set(news_thumbnail_dict[news_id]))
            if list_len != set_len:
                invalid_newsid_list.add(news_id)

        # 删除图片有问题的新闻
        valid_news_list = []
        for news in self.news_list:
            if news['id'] not in invalid_newsid_list:
                valid_news_list.append(news)
        self.news_list = valid_news_list

    def upload_image(self):
        # 5. 上传图片到oss
        for img_url in self.need_down_image_list:
            img_info = self.need_down_image_list[img_url]
            if img_info['down_status']:
                local_file = img_info['local_file']
                remote_file = 'app/hippo-n/%s/%s.%s' % (
                    self.date_dir_name, img_info['md5'], img_info['format'])
                # self.OSSKit.upload(local_file, remote_file)
                img_info['remote_file'] = remote_file

        # 替换新闻图片->cdn图片地址
        for news in self.news_list:
            news['img_md5'] = []
            # 缩略图
            for img in news['images']:
                raw_url = img['url']
                img_info = self.need_down_image_list[raw_url]
                cdn_url = self.cdn_host + img_info['remote_file']
                img['url'] = cdn_url
                # 存入缩略图md5
                news['img_md5'].append(img_info['file_md5'])

            # 详情图片
            for line in news['detail']:
                if type(line) == dict:
                    raw_url = line['url']
                    img_info = self.need_down_image_list[raw_url]
                    cdn_url = self.cdn_host + img_info['remote_file']
                    line['url'] = cdn_url

        # 删除本地下载的图片文件夹
        shutil.rmtree(self.image_download_dir, True)

    def category_mapping(self):
        # 6. 频道映射
        new_news_list = []
        for news in self.news_list:
            source_cat = None
            if self.newsid_prefix in CategoryMap:
                if news['cat'] in CategoryMap[self.newsid_prefix]:
                    source_cat = CategoryMap[self.newsid_prefix][news['cat']]
            if source_cat:
                news['cat'] = source_cat
                new_news_list.append(news)
            else:
                print('no source_cat')
                print(json.dumps(news, ensure_ascii=False))

        self.news_list = new_news_list

    def save_into_mongodb(self):
        # 6. 存入mongodb
        new_news_list = []
        for news in self.news_list:
            ok = self.mongo_client.save(news)
            if ok:
                new_news_list.append(news)

        self.news_list = new_news_list

    def get_home_news_list(self):
        # 提取推荐频道新闻列表
        # TODO
        return self.news_list

    def save_into_redis(self):
        # 7. 存入redis
        # 7.1. 存入推荐列表
        self.home_news_list = self.get_home_news_list()
        self.redis_client.save_home_news_list(self.home_news_list)
        # 7.2. 存入其他频道列表
        self.redis_client.save_chn_news_list(self.news_list)
        # 7.3. 存入标签列表
        self.redis_client.save_tag_list(self.news_list)

    def process(self):
        # 0. 生成新闻id
        self.gen_newsid()

        self.filter_no_images_news()

        # 1. 生成标签
        self.gen_tags()

        # 2. 去重
        self.remove_duplicate()

        # 3. 下载图片
        self.download_image()

        # 4. 过滤
        self.filter_invalid()

        # 5. 图片上传
        # self.upload_image()

        # 6. 映射频道
        self.category_mapping()

        # 7. 存入mongodb
        # self.save_into_mongodb()

        # 8. 存入redis
        # self.save_into_redis()

        return self.news_list
