"""
使用 redis 维护一个请求队列
"""
from pickle import dumps, loads
from redis import StrictRedis
from ItOrange.search.config import *
from ItOrange.search.request import ItJuZiRequest


class RedisQueue(object):
    def __init__(self):
        """
        初始化Redis
        """
        self.db = StrictRedis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD)

    def add(self, request):
        """
        向队列中添序列化后的 Request
        :param request:
        :return:
        """
        if isinstance(request, ItJuZiRequest):
            self.db.rpush(REDIS_KEY, dumps(request))
        return False

    def pop(self):
        """
        取出一个请求，并反序列化
        :return:
        """
        # 判断队列是否为空
        if self.db.llen(REDIS_KEY):
            return loads(self.db.lpop(REDIS_KEY))
        else:
            return False

    def clear(self):
        """
        清空请求
        :return:
        """
        self.db.delete(REDIS_KEY)

    def empty(self):
        """
        判断队列是否为空
        :return:
        """
        return self.db.llen(REDIS_KEY) == 0
