"""
这是 IT 桔子爬虫的一个功能模块，使用 requests 实现了一个能根据用户输入的关键字去查询的功能
将根据关键字搜索的结果展示给用户，主要包含以下几部分：
1、公司     --------------> company
2、创业者   --------------> person
3、投资机构 -------------->invst
4、投资人   -------------->invsp
5、专辑     -------------->album
7、新闻     -------------->news
8、报告     -------------->report
用户可以根据以上各部分的搜索结果，选择需要抓取的信息，也同样支持将以上信息全部抓取
目前失败在构造完成请求后在请求时总是405,但是使用request请求可以成功
"""
import json
from urllib import parse
import requests
from requests import Session, ReadTimeout
from ItOrange.proxy.db import REDISCLIENT
from ItOrange.search.config import MAX_FAILED_TIME, VALID_STATUSES
from ItOrange.search.db import RedisQueue
from ItOrange.search.request import ItJuZiRequest


class ITjuziSpider(object):
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczpcL1wvd3d3Lml0anV6aS5jb21cL'
                         '2FwaVwvdXNlcnNcL3VzZXJfaGVhZGVyX2luZm8iLCJpYXQiOjE1NTc0NTQ5NTYsImV4cCI6MTU1NzQ3NDE4NSwibmJmI'
                         'joxNTU3NDcwNTg1LCJqdGkiOiJpQUJldnR4a2VvNnFKSDFUIiwic3ViIjo3MjIyNzksInBydiI6IjIzYmQ1Yzg5NDlmN'
                         'jAwYWRiMzllNzAxYzQwMDg3MmRiN2E1OTc2ZjcifQ.ldgbYyAU0_7qWVoKeZQTkUv12Mp6YdumZ5PZbb2-MDI',
        'Connection': 'keep-alive',
        'Cookie': 'juzi_user=722279; acw_tc=76b20f6a15574548296717159e4f4872cfe50e073321a3c58aeb8664cba4bd; _uab_col'
                  'lina=155745483432025313066631; _ga=GA1.2.205912705.1557454838; _gid=GA1.2.2143363481.1557454838; '
                  'Hm_lvt_1c587ad486cdb6b962e94fc2002edf89=1557454838; juzi_token=Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJ'
                  'IUzI1NiJ9.eyJpc3MiOiJodHRwczpcL1wvd3d3Lml0anV6aS5jb21cL2FwaVwvdXNlcnNcL3VzZXJfaGVhZGVyX2luZm8iLCJ'
                  'pYXQiOjE1NTc0NTQ5NTYsImV4cCI6MTU1NzQ3NDE4NSwibmJmIjoxNTU3NDcwNTg1LCJqdGkiOiJpQUJldnR4a2VvNnFKSDFUI'
                  'iwic3ViIjo3MjIyNzksInBydiI6IjIzYmQ1Yzg5NDlmNjAwYWRiMzllNzAxYzQwMDg3MmRiN2E1OTc2ZjcifQ.ldgbYyAU0_7q'
                  'WVoKeZQTkUv12Mp6YdumZ5PZbb2-MDI; Hm_lpvt_1c587ad486cdb6b962e94fc2002edf89=1557470903',
        'Host': 'www.itjuzi.com',
        'Referer': 'https://www.itjuzi.com/search?data=%E4%BB%8A%E6%97%A5%E5%A4%B4%E6%9D%A1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/'
                      '537.36 (KHTML, like Gecko) Chrome/72.0.3626.109 Safari/537.36',
    }
    # 首次请求的URL，需要提供搜索关键字 keyword
    first_url = "https://www.itjuzi.com/api/search/index_search?word={keyword}"
    # 各个分区的请求链接，页号从1开始传递，type 传入上述字典类型
    company_url = "https://www.itjuzi.com/api/search/index_search?word={}&page={}&type[]={}"
    # session 对象
    session = Session()
    # 请求队列
    queue = RedisQueue()
    # proxy pool 对象
    db = REDISCLIENT()

    def get_proxy(self):
        """
        获取随机的有效的代理
        :return:
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
                self.get_proxy()
        except requests.ConnectionError:
            return False

    def send_request(self, itJuZi_request):
        """
        处理请求，获取响应
        :param itJuZi_request:
        :return:
        """
        try:
            # 更新 Headers
            self.session.headers.update(self.headers)
            print(self.session.headers)
            # 判断该请求是否需要使用代理
            if itJuZi_request.need_proxy:
                # 获取随机的有效的代理
                proxy = self.get_proxy()
                if proxy:
                    proxies = {
                        'http': 'http://' + proxy,
                        'https': 'https://' + proxy
                    }
                    # 将响应返回
                    return self.session.send(itJuZi_request.prepare(),
                                             timeout=itJuZi_request.timeout, allow_redirects=False, proxies=proxies)
            # 不需使用代理
            return self.session.send(itJuZi_request.prepare(),
                                     timeout=itJuZi_request.timeout, allow_redirects=False)
        except (ConnectionError, ReadTimeout) as e:
            print(e.args)
            return False

    def error(self, itJuZi_request):
        """
        对失败的请求进行标记
        :param itJuZi_request: 请求
        :return:
        """
        # 将请求失败的次数自增
        itJuZi_request.fail_time += 1
        print('Request Failed', itJuZi_request.fail_time, 'Times', itJuZi_request.url)
        # 判断是否在重试范围内
        if itJuZi_request.fail_time < MAX_FAILED_TIME:
            # 重新加入请求队列
            self.queue.add(itJuZi_request)

    def start(self):
        """
        根据用户输入的关键字构造初始请求，并加入请求队列等待调度
        :return:
        """
        # 获取用户搜索关键字
        keyword = input("请输入你要查询的关键字：\n")
        # 构造初始URl
        start_url = self.first_url.format(keyword=parse.quote(keyword))
        itJuZi_request = ItJuZiRequest(url=start_url, need_proxy=False, callback=self.parse)
        # 将请求加入请求队列
        self.queue.add(itJuZi_request)

    def parse(self, response):
        """
        解析获取的响应，为Json, 共分七部分组成需要单独的对每一项进行解析
        :param response:
        :return:
        """
        # 将获取的Json 数据转换成字典
        result = json.loads(response.text)
        # status 为 success 不代表获取了数据，所以判断响应的状态码
        if result.get("code") == 200:
            # 获取各部分的搜索结果
            company_total = result.get("data").get("company").get("page")
            person_total = result.get("data").get("person").get("page")
            invst_total = result.get("data").get("invst").get("page")
            invsp_total = result.get("data").get("invsp").get("page")
            album_total = result.get("data").get("album").get("page")
            news_total = result.get("data").get("news").get("page")
            report_total = result.get("data").get("report").get("page")
            print(
                """
            查询结果如下：\n
            公司（company）   ：{0}\n
            创业者（person）  ：{1}\n
            投资机构（invst） ：{2}\n
            投资人（invsp）   ：{3}\n
            专辑（album）     ：{4}\n
            新闻（news）      ：{5}\n
            报告（report）    ：{6}\n
            """.format(company_total, person_total, invst_total, invsp_total, album_total, news_total, report_total))
            return company_total, person_total, invst_total, invsp_total, album_total, news_total, report_total

    def schedule(self):
        """
        调度请求
        :return:
        """
        while not self.queue.empty():
            itJuZi_request = self.queue.pop()
            callback = itJuZi_request.callback
            print('Schedule', itJuZi_request.url)
            response = self.send_request(itJuZi_request)
            print("查看获取的响应：", response)
            if response and response.status_code in VALID_STATUSES:
                result = callback(response)
                print(result)


# 测试代码
if __name__ == "__main__":
    itJuZi = ITjuziSpider()
    itJuZi.start()
    itJuZi.schedule()
