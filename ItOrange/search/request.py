"""
自定义的请求类，在这里构造请求对象
"""
from requests import Request
from ItOrange.search.config import *


class ItJuZiRequest(Request):
    """
    通过继承 request.Request 类来构造请求对象
    """
    def __init__(self, url, callback, method="GET", headers=None, need_proxy=False, fail_time=0, timeout=TIMEOUT):
        """

        :param url: 请求的URL
        :param callback: 回调函数
        :param method: 默认 GET 请求
        :param headers: 默认无请求头
        :param need_proxy: 默认不使用代理
        :param fail_time: 失败重试次数
        :param timeout: 超时时间
        """
        Request.__init__(self, method, url, headers)
        self.callback = callback
        self.need_proxy = need_proxy
        self.fail_time = fail_time
        self.timeout = timeout
