import urllib
import re
import json
from random import choice
from scrapy.spiders import Spider
from scrapy.http import FormRequest
from scrapy import Request

from .lib import  lib_parse_subject_detail

class DoubanCartoonSubject(Spider):

    def __init__(self, score=0,
        fmt_str='https://movie.douban.com/j/new_search_subjects?tags=动画&range=%.1f,%.1f&start=0'):
        self.subject_set = set()
        self.url_list = []
        self.fmt_str = fmt_str
        self.score = score
        while self.score <= 10:
            url = self.fmt_str % (self.score, self.score)
            self.url_list.append(url)
            self.score += 0.1

    name = 'cartoons'

    def start_requests(self):
        self.logger.warning("start_request 请求入口")
        self.logger.warning(self.url_list)
        for url in self.url_list:
            yield Request(url)


    def parse(self, response):
        if response.status == 200:
            url = response.url
            res = json.loads(response.body_as_unicode())
            data = res.get('data')
            if data:
                for d in data:
                    subject_id = d.get('id')
                    self.subject_set.add(subject_id)
                    detail_url = d.get('url')
                    item = {
                        'detail_url': detail_url,
                        'subject_id': subject_id,
                        'category': '动画'
                    }
                    yield Request(
                            detail_url,
                            callback=self.parse_movie_detail,
                            meta={'item': item},
                            dont_filter=True)
                # 翻页
                url = url.split('=')
                url[-1] = str(int(url[-1]) + 20)
                url = '='.join(url)
                yield Request(url)
            else:
                self.logger.warning('没有数据：{}'.format(url))
        else:
            self.logger.error(response.url)
            self.logger.error('状态码为：{}'.format(response.status))

    def parse_movie_detail(self, response):
        return lib_parse_subject_detail(self, response)



