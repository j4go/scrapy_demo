import urllib
import re
import time
from random import choice
from scrapy.spiders import Spider
from scrapy.http import FormRequest
from scrapy import Request

from .lib import  lib_parse_subject_detail

class DoubanGetTop250Info(Spider):

    name = 'top250'

    start_urls = ['https://movie.douban.com/top250?start=' + str(i)
                    for i in range(250) if i % 25 == 0]

    def parse(self, response):
        self.logger.warning("进入parse处理")
        res_infos = response.css('div.info')
        for res in res_infos:
            # 电影详情页的url
            url_con_str = res.css('a').extract_first()
            url_re = re.compile('"(.*?)"')  # 双引号之间即是url
            url = url_re.findall(url_con_str)
            if url:
                url = url[0]
                if url:
                    item = {
                        'detail_url': url,
                        'category': '电影'
                    }
                    self.logger.warning("获得subject链接，跳往详情页")
                    yield Request(
                            item['detail_url'],
                            callback=self.parse_movie_detail,
                            meta={'item': item},
                            dont_filter=True)

    def parse_movie_detail(self, response):
        return lib_parse_subject_detail(self, response)

