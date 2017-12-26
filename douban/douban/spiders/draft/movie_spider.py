import scrapy
import re


class Movie(scrapy.Spider):

    name = "movie"
    allowed_domains = ["douban.com"]

    start_urls = (
        'https://movie.douban.com/subject/1291841/', # 教父
        'https://movie.douban.com/subject/1299131/', # 教父2
        'https://movie.douban.com/subject/1292052/', # 肖申克的救赎
    )

    def parse(self, response):
        # item = DoubanItem()
        r = response.css('h1 span::text').extract()
        # item['name'] = r[0]
        # item['year'] = r[1]
        # yield item
        self.logger.info(str(r[0]))
        self.logger.info(str(r[1]))
