"""
此方法未来作为 scrapy 的 spider 下载中间件的一个方法使用，保证获取的是有效的代理
将此方法在下载中间件中重写后删除该文件即可
"""
import requests


def get_random_proxy(self):
    """
    连接数据库
    保证获取随机有效的proxy
    :return: proxy
    """
    # 获取代理ip
    try:
        # 获取随机的代理
        proxy = self.db.random()
        # 顺便检查一下代理数量是否达到阈值
        self.db.check()
        # 增加添加代理前的检测环节，保证获取的代理有效
        if proxy:
            ip = proxy.split(":")[0]
            port = proxy.split(":")[1]
            if self.db.check_proxy(ip, port):
                return proxy
        else:  # 回调自己重新获取代理
            self.get_random_proxy()
    except requests.ConnectionError:
        return False
