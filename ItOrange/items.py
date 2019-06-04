# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ItorangeItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # 公司信息
    company_info = scrapy.Field()


class SearchResultItem(scrapy.Item):
    # 搜索关键字
    keyword = scrapy.Field()
    # 分支
    type = scrapy.Field()
    # 搜索结果
    data = scrapy.Field()


