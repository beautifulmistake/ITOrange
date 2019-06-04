"""
该爬虫是IT 橘子爬虫，主要抓取公司的相关信息
需要说明的是：
1、此次的响应的数为 Json
2、请求为 Ajax POST 请求
3、请求的参数为 request payload 类型 ，具体的请自行百度它与 formdata 这种参数传递时的区别
4、发送参数时一定注意不能使用 FormRequest 发送，这个只是适用于 formdata 这种参数类型
5、此次在发送请求参数时采用了 Request 的发送方法，在使用时特别需要注意的时以下几点：
    1、Content-Type  必须使用：application/json;charset=UTF-8
    2、参数传递使用 body= json类型的参数（json.dumps，把该参数变成json格式的数据）
    3、method= 'POST'
    4、注意其中一些参数是 null的 和 None 的，这个视情况而定，此次的参数没有的按照浏览器抓包的结果 作为 ""  空处理了
6、另外走的一个冤枉路就是：有时候参数全部携带不一定是一件好事儿，有时候偏偏获取不到数据,此次如果不携带Authorization只能获取一页的数据，cookies 中有一项 juzi_token 值

"""
import json
import os

import scrapy
from scrapy.exceptions import CloseSpider
from scrapy.signals import spider_closed
from scrapy.spidermiddlewares.httperror import HttpError
from scrapy_redis.spiders import RedisSpider
from twisted.internet.error import TCPTimedOutError, DNSLookupError

from ItOrange.items import ItorangeItem


class ItOrange(RedisSpider):
    name = 'itOrange'   # 爬虫名称
    redis_key = 'ItOrange: items'   # redis_key

    def __init__(self, settings):
        super().__init__()
        # 记录列表页信息
        self.record_file = open(os.path.join(settings.get("JSON_PATH"), f'{self.name}.json'), "a+", encoding='utf-8')
        self.record_file.write('[')
        self.keyword_file_list = os.listdir(settings.get("KEYWORD_PATH"))
        # 请求地址
        self.base_url = "https://www.itjuzi.com/api/companys"
        # 请求头
        self.headers = {
            'Content-Type': 'application/json;charset=UTF-8',
            'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczpcL1wvd3d3Lml0anV6aS5jb21'
                             'cL2FwaVwvdXNlcnNcL3VzZXJfaGVhZGVyX2luZm8iLCJpYXQiOjE1NTcyOTU1OTgsImV4cCI6MTU1NzMxMjk2OS'
                             'wibmJmIjoxNTU3MzA5MzY5LCJqdGkiOiJDNXBCeHV3VnpHRzhVM2RzIiwic3ViIjo3MjIyNzksInBydiI6IjIz'
                             'YmQ1Yzg5NDlmNjAwYWRiMzllNzAxYzQwMDg3MmRiN2E1OTc2ZjcifQ.OJdKLoKYOVycCXdEDOznfjNUz'
                             'lHub6yIBG1CtdKzZUM',
            'Cookie': 'acw_tc=781bad0615571207746187293e1ffb4b5751067778f56b02e94378e54732ba;'
                      ' _ga=GA1.2.1301463971.1557120777; Hm_lvt_1c587ad486cdb6b962e94fc2002edf89='
                      '1557120783,1557120917; juzi_user=722279; _gid=GA1.2.961721702.1557281427; '
                      'juzi_token=bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczpcL'
                      '1wvd3d3Lml0anV6aS5jb21cL2FwaVwvYXV0aG9yaXphdGlvbnMiLCJpYXQiOjE1NTcyOTU1OTgsI'
                      'mV4cCI6MTU1NzI5OTE5OCwibmJmIjoxNTU3Mjk1NTk4LCJqdGkiOiIyTDluN2NXZG9lWFVza3BCI'
                      'iwic3ViIjo3MjIyNzksInBydiI6IjIzYmQ1Yzg5NDlmNjAwYWRiMzllNzAxYzQwMDg3MmRiN2E1O'
                      'Tc2ZjcifQ.YUKLNxd9sZxoBEedzKaw3oePIYFLI8TVvMPenD0C80I; Hm_lpvt_1c587ad486cdb'
                      '6b962e94fc2002edf89=1557300772',
            'Host': 'www.itjuzi.com',
            'Origin': 'https://www.itjuzi.com',
            'Referer': 'https://www.itjuzi.com/company',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, '
                          'like Gecko) Chrome/72.0.3626.109 Safari/537.36'
        }

    def parse_err(self, failure):
        """
        处理各种异常，将请求失败的Request自定义处理方式
        :param failure:
        :return:
        """
        if failure.check(TimeoutError, TCPTimedOutError, DNSLookupError):
            request = failure.request
            self.server.rpush(self.redis_key, request)
        if failure.check(HttpError):
            response = failure.value.response
            self.server.rpush(self.redis_key, response.url)
        return

    def start_requests(self):
            """
            生成初始请求
            :return:
            """
            # 判断关键字文件是否存在
            if not self.keyword_file_list:
                # 抛出异常
                raise CloseSpider("需要关键字文件")
            for keyword_file in self.keyword_file_list:
                # 获取关键字文件路径
                file_path = os.path.join(self.settings.get("KEYWORD_PATH"), keyword_file)
                # 读取文件
                with open(file_path, 'r', encoding='utf-8') as f:
                    for keyword in f.readlines():
                        # 消除末尾的空白字符
                        keyword = keyword.strip()
                        print(keyword)
                        # 发起请求
                        yield scrapy.Request(url=self.base_url, headers=self.headers,
                                             callback=self.parse, errback=self.parse_err,
                                             dont_filter=True, method='POST', body=keyword)

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        # 获取配置信息
        settings = crawler.settings
        # 爬虫信息
        spider = super(ItOrange, cls).from_crawler(crawler, settings, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=spider_closed)
        return spider

    def spider_closed(self, spider):
        # 输出日志关闭爬虫
        self.logger.info('Spider closed：%s', spider.name)
        spider.record_file.write("]")
        spider.record_file.close()

    def parse(self, response):
        """
        解析响应
        :param response:
        :return:
        """
        if response.status == 200:
            print(response.text)
            # 创建item
            item = ItorangeItem()
            # 将获取的 json 转换为 字典
            result = json.loads(response.text, encoding='utf-8')
            # 获取响应的状态
            status = result.get("status")
            if status == "success":
                # 获取当前采集的页号
                page = result.get("data").get("page").get("page")
                # 获取每一页的20条数据，为一个列表，每一条就是一个公司信息
                res = {
                    "status": status,
                    "page": page
                }
                self.record_file.write(json.dumps(res, ensure_ascii=False) + "\n")
                datas = result.get('data').get('data')
                # 将获取的数据写入文件
                for data in datas:
                    item['company_info'] = data
                    yield item
                    # 每一天数据是字典，序列化之后写入文件
                    # self.record(data)

    def record(self, data):
        """
        将二级分类的列表信息写入文件:字典转json
        :param data:
        :return:
        """
        with open(r'F:\project\ItOrange\ItOrange\record\company_info.json', 'a+', encoding="utf-8") as f:
            if isinstance(data, dict):
                # 将字典的数据转为json
                result = json.dumps(data, ensure_ascii=False)
                # 将结果写入文件
                f.write(result + "\n")





