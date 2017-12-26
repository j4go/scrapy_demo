import scrapy
import re
from douban.items import ImdbTopItem


class Imdb(scrapy.Spider):

    def __init__(self):
        self.start = 0

    name = "imdb"
    allowed_domains = ["imdb.com"]
    start_urls = [
        'http://www.imdb.com/chart/top', # imdb top250
    ]

    def parse(self, response):
        item = ImdbTopItem()
        res_infos = response.css('tbody.lister-list tr')

        for res in res_infos:
            tmp = {}
            title = res.css('td.titleColumn a::text').extract_first() # 电影名称
            item['title'] = title
            score_and_count = res.css('td strong').extract_first() # 电影评分和评分人数
            score_and_count = score_and_count.split('"')[1].split()
            score = score_and_count[0]
            count = score_and_count[3].replace(',','')
            item['score'] = float(score)
            item['count'] = int(count)
            yield item

        


        