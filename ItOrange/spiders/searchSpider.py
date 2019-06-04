"""
搜索爬虫,根据关键字进行搜索
"""
import json
import os
import scrapy
from scrapy.exceptions import CloseSpider
from scrapy.signals import spider_closed
from scrapy.spidermiddlewares.httperror import HttpError
from scrapy_redis.spiders import RedisSpider
from twisted.internet.error import TCPTimedOutError, DNSLookupError

from ItOrange.items import SearchResultItem


class SearchSpider(RedisSpider):
    name = "search"
    redis_key = "SearchSpider:items"

    def __init__(self, settings):
        super().__init__()
        self.keyword_file_list = os.listdir(settings.get("KEYWORD_PATH"))
        # 首次请求的URL，需要提供搜索关键字 keyword
        self.first_url = "https://www.itjuzi.com/api/search/index_search?word={keyword}"
        # 各个分区的请求链接，页号从1开始传递，type 传入上述字典类型
        self.branch_url = "https://www.itjuzi.com/api/search/index_search?word={}&page={}&type[]={}"
        # 请求头
        self.headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczpcL1wvd3d3Lml0anV6aS5'
                             'jb21cL2FwaVwvdXNlcnNcL3VzZXJfaGVhZGVyX2luZm8iLCJpYXQiOjE1NTc0NTQ5NTYsImV4cCI6MTU1Nz'
                             'Q3NDE4NSwibmJmIjoxNTU3NDcwNTg1LCJqdGkiOiJpQUJldnR4a2VvNnFKSDFUIiwic3ViIjo3MjIyNzksIn'
                             'BydiI6IjIzYmQ1Yzg5NDlmNjAwYWRiMzllNzAxYzQwMDg3MmRiN2E1OTc2ZjcifQ.ldgbYyAU0_7qWVoKeZQ'
                             'TkUv12Mp6YdumZ5PZbb2-MDI',
            'Connection': 'keep-alive',
            'Cookie': 'juzi_user=722279; acw_tc=76b20f6a15574548296717159e4f4872cfe50e073321a3c58aeb8664cba4bd;'
                      ' _uab_collina=155745483432025313066631; _ga=GA1.2.205912705.1557454838; _gid=GA1.2.2143363481'
                      '.1557454838; Hm_lvt_1c587ad486cdb6b962e94fc2002edf89=1557454838; juzi_token=Bearer eyJ0eXAiOi'
                      'JKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczpcL1wvd3d3Lml0anV6aS5jb21cL2FwaVwvdXNlcnNcL3VzZX'
                      'JfaGVhZGVyX2luZm8iLCJpYXQiOjE1NTc0NTQ5NTYsImV4cCI6MTU1NzQ3NDE4NSwibmJmIjoxNTU3NDcwNTg1LCJqdGk'
                      'iOiJpQUJldnR4a2VvNnFKSDFUIiwic3ViIjo3MjIyNzksInBydiI6IjIzYmQ1Yzg5NDlmNjAwYWRiMzllNzAxYzQwMDg3'
                      'MmRiN2E1OTc2ZjcifQ.ldgbYyAU0_7qWVoKeZQTkUv12Mp6YdumZ5PZbb2-MDI; Hm_lpvt_1c587ad486cdb6b962e94'
                      'fc2002edf89=1557470903',
            'Host': 'www.itjuzi.com',
            'Referer': 'https://www.itjuzi.com/search?data=%E4%BB%8A%E6%97%A5%E5%A4%B4%E6%9D%A1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/'
                          '537.36 (KHTML, like Gecko) Chrome/72.0.3626.109 Safari/537.36',
            }
        # 初始页号
        self.start_page = 1
        # 全局的默认值
        self.default_value = "暂无"

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
                        yield scrapy.Request(url=self.first_url.format(keyword=keyword), headers=self.headers,
                                             callback=self.parse, errback=self.parse_err, meta={"keyword": keyword})

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        # 获取配置信息
        settings = crawler.settings
        # 爬虫信息
        spider = super(SearchSpider, cls).from_crawler(crawler, settings, *args, **kwargs)
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
            # 将获取的 json 转换为 字典
            result = json.loads(response.text, encoding='utf-8')
            # 获取响应的状态码
            code = result.get("code")
            # 搜索关键字
            keyword = response.meta["keyword"]
            if code == 200:
                # 获取各项的搜索结果
                company_total = result.get("data").get("company").get("page").get("total")    # 公司
                person_total = result.get("data").get("person").get("page").get("total")    # 创业者
                invst_total = result.get("data").get("invst").get("page").get("total")  # 投资机构
                invsp_total = result.get("data").get("invsp").get("page").get("total")  # 投资人
                album_total = result.get("data").get("album").get("page").get("total")  # 专辑
                news_total = result.get("data").get("news").get("page").get("total")    # 新闻
                report_total = result.get("data").get("report").get("page").get("total")    # 报告
                result = {
                    "keyword": keyword,
                    "company": company_total,
                    "person": person_total,
                    "invst": invst_total,
                    "invsp": invsp_total,
                    "album": album_total,
                    "news": news_total,
                    "report": report_total
                }
                # 请求公司信息 word page type
                if company_total != 0:
                    yield scrapy.Request(url=self.branch_url.format(keyword, self.start_page, "company"),
                                         callback=self.parse_common, errback=self.parse_err, headers=self.headers,
                                         meta={"keyword": keyword, "type": "company"})
                # 请求创业者的信息
                if person_total != 0:
                    yield scrapy.Request(url=self.branch_url.format(keyword, self.start_page, "person"),
                                         callback=self.parse_common, errback=self.parse_err, headers=self.headers,
                                         meta={"keyword": keyword, "type": "person"})
                # 请求投资机构的信息
                if invst_total != 0:
                    yield scrapy.Request(url=self.branch_url.format(keyword, self.start_page, "invst"),
                                         callback=self.parse_common, errback=self.parse_err, headers=self.headers,
                                         meta={"keyword": keyword, "type": "invst"})
                # 请求投资人的信息
                if invsp_total != 0:
                    yield scrapy.Request(url=self.branch_url.format(keyword, self.start_page, "invsp"),
                                         callback=self.parse_common, errback=self.parse_err, headers=self.headers,
                                         meta={"keyword": keyword, "type": "invsp"})
                # 请求专辑信息
                if album_total != 0:
                    yield scrapy.Request(url=self.branch_url.format(keyword, self.start_page, "album"),
                                         callback=self.parse_common, errback=self.parse_err, headers=self.headers,
                                         meta={"keyword": keyword, "type": "album"})
                # 请求新闻信息
                if news_total != 0:
                    yield scrapy.Request(url=self.branch_url.format(keyword, self.start_page, "news"),
                                         callback=self.parse_common, errback=self.parse_err, headers=self.headers,
                                         meta={"keyword": keyword, "type": "news"})
                # 请求报告信息
                if report_total != 0:
                    yield scrapy.Request(url=self.branch_url.format(keyword, self.start_page, "report"),
                                         callback=self.parse_common, errback=self.parse_err, headers=self.headers,
                                         meta={"keyword": keyword, "type": "report"})
                # 将搜索结果存入文件
                self.record(result)

    def parse_common(self, response):
        """
        七个分支公用的一个解析响应的方法,需要从 meta 中获取 type
        :param response:
        :return:
        """
        if response.status == 200:
            # 创建 item
            item = SearchResultItem()
            # 将获取的 json 转换为 字典
            result = json.loads(response.text, encoding='utf-8')
            # 获取响应的状态码
            code = result.get("code")
            # 搜索关键字
            keyword = response.meta["keyword"]
            # 获取搜索类型
            type = response.meta["type"]
            if code == 200:
                # 获取当前的 page
                page = result.get("data").get(type).get("page").get("page")
                # 获取 总数据量
                total = result.get("data").get(type).get("page").get("total")
                # 获取数据
                data = result.get("data")
                item['keyword'] = keyword if keyword else self.default_value
                item['type'] = type if type else self.default_value
                item['data'] = data if data else self.default_value
                yield item
                # 判断是否有下一页
                if page * 10 < total:
                    page += 1
                    yield scrapy.Request(url=self.branch_url.format(keyword, page, type),
                                         callback=self.parse_common, errback=self.parse_err, headers=self.headers,
                                         meta={"keyword": keyword, "type": type})

    def record(self, data):
        """
        将二级分类的列表信息写入文件:字典转json
        :param data:
        :return:
        """
        with open(r'F:\project\IT_Orange\ItOrange\record\search_result.json', 'a+', encoding="utf-8") as f:
            if isinstance(data, dict):
                # 将字典的数据转为json
                result = json.dumps(data, ensure_ascii=False)
                # 将结果写入文件
                f.write(result + "\n")
