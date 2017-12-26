import scrapy
import urllib
import re
import time
from random import choice
from scrapy.spiders import Spider
from scrapy.http import FormRequest
from douban.items import DoubanMovieTop250Item


class DoubanGetInfoNoDetail(Spider):

    def __init__(self, username, nickname, password):
        self.top_num = 0
        self.username = username
        self.nickname = nickname
        self.password = password

    name = 'douban_get_info_no_detail'

    start_urls = ['https://movie.douban.com/top250?start=' + str(i)
                    for i in range(250) if i % 25 == 0]

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            username = crawler.settings.get('DOUBAN_USERNAME'),
            nickname = crawler.settings.get('DOUBAN_NICKNAME'),
            password = crawler.settings.get('DOUBAN_PASSWORD')
        )

    def parse(self, response):
        self.logger.warning("进入parse处理")
        res_infos = response.css('div.info')
        for res in res_infos:
            item = DoubanMovieTop250Item()
            hd = res.css('div.hd') # 电影名称
            movie_title_list = hd.css('span::text').extract()
            # "".join(m.split()) 去除\xa0(也就是&nbsp;)
            item['full_name'] = ''.join("".join(m.split()) for m in movie_title_list[:-1])
            item['name'] = item['full_name'].split('/')[0]
            bd = res.css('div.bd') # 电影评分和评分人数
            score_and_count = bd.css('div.star span::text').extract()
            score = score_and_count[0]
            count = score_and_count[1]
            item['score'] = float(score)
            regex = re.compile('^[0-9]*')
            count_str = regex.findall(count)[0] # 取出数字字符串
            item['count'] = int(count_str)
            self.top_num += 1
            item['top_num'] = self.top_num
            item['movie_intro'] = ''
            item['detail_url'] = ''
            yield item



