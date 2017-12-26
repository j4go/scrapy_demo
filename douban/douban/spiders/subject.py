import urllib
import re
from random import choice
from scrapy.spiders import Spider
from scrapy.http import FormRequest
from scrapy import Request

from .lib import  lib_parse_subject_detail

class DoubanGetOneMovieInfo(Spider):
    name = 'subject'

    # 战狼2 https://movie.douban.com/subject/26363254/
    # 夏洛克 https://movie.douban.com/subject/3986493/
    start_urls = ['https://movie.douban.com/subject/1309046/']

    def parse(self, response):
        self.logger.warning("进入parse处理")
        if response.status == 200:
            url = response.url
            item = {
                'detail_url': url,
                'category': '电影'
            }
            self.logger.warning("获得subject链接，跳往详情页")
            yield Request(
                url,
                callback=self.parse_movie_detail,
                meta={'item': item},
                dont_filter=True)
        else:
            self.logger.error(response.url)
            self.logger.error('状态码为：{}'.format(response.status))


    def parse_movie_detail(self, response):
        return lib_parse_subject_detail(self, response)



