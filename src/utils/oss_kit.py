# coding:utf-8
import oss2


class OSSKit:

    def __init__(self):
        self.AccessKeyID = ''
        self.AccessKeySecret = ''
        self.bucket_name = ''
        self.bucket_endpoint = ''
        self.bucket = self.get_bucket()

    def get_bucket(self):
        auth = oss2.Auth(self.AccessKeyID, self.AccessKeySecret)
        bucket = oss2.Bucket(auth, self.bucket_endpoint, self.bucket_name)
        return bucket

    def upload(self, local_file, remote_file):
        # 上传文件
        res = self.bucket.put_object_from_file(remote_file, local_file)
