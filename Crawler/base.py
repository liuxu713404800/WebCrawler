import requests
import urllib

class webRequest:

    # 创建默认对象值
    def __init__(self, url = '', http_fun = 'GET',  header = {}, proxy = 1):
        #将个变量赋值给对象
        self.url = url
        self.http_fun = http_fun
        self.header = header
        self.proxy = proxy
