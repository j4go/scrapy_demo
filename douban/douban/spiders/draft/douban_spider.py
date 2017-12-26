import scrapy
import re
from douban.items import DoubanItem, DoubanTopItem


class Douban(scrapy.Spider):

    def __init__(self):
        self.start = 0

    name = "douban"
    allowed_domains = ["douban.com"]
    start_urls = [
        'https://movie.douban.com/top250?start=0', # 豆瓣top250
    ]

    # start_urls = [
    #     'https://movie.douban.com/subject/1291841/', # 教父
    #     'https://movie.douban.com/subject/1299131/', # 教父2
    #     'https://movie.douban.com/subject/1292052/', # 肖申克的救赎
    # ]

    # def parse(self, response):
    #     item = DoubanItem()
    #     r = response.css('h1 span::text').extract()
    #     item['name'] = r[0]
    #     item['year'] = r[1]
    #     yield item

    def parse(self, response):
        item = DoubanTopItem()
        res_infos = response.css('div.info')

        for res in res_infos:
            tmp = {}
            hd = res.css('div.hd') # 电影名称
            movie_title_list = hd.css('span::text').extract()
            # "".join(m.split()) 去除\xa0(也就是&nbsp;)
            item['title'] = ''.join("".join(m.split()) for m in movie_title_list[:-1])
            bd = res.css('div.bd') # 电影评分和评分人数
            score_and_count = bd.css('div.star span::text').extract()
            score = score_and_count[0]
            count = score_and_count[1]
            item['score'] = float(score)
            regex = re.compile('^[0-9]*')
            count_str = regex.findall(count)[0] # 取出数字字符串
            item['count'] = int(count_str)
            yield item

        self.start += 25
        while self.start <= 225:
            next_page = 'https://movie.douban.com/top250?start=' + str(self.start)
            yield scrapy.Request(next_page, callback=self.parse)



