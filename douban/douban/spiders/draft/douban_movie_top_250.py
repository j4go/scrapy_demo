
import re
import scrapy
from douban.items import DoubanMovieTop250Item, DoubanMovieDetail


class DoubanMovieTop250(scrapy.Spider):

    def __init__(self):
        self.start = 0
        self.top_num = 0

    name = "douban_movie_top_250"

    start_urls = [
        'https://movie.douban.com/top250?start=0'
    ]

    def parse(self, response):
        res_infos = response.css('div.info')
        for res in res_infos:
            item = {}
            tmp = {}
            # 电影详情页的url
            url_con_str = res.css('a').extract_first()
            url_re = re.compile('"(.*?)"')
            url = url_re.findall(url_con_str)
            item['detail_url'] = url[0]
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
            item['count'] = count_str # int(count_str)
            self.top_num += 1
            item['top_num'] = self.top_num
            # self.logger.error("item['score']", type(item['score']))
            # self.logger.error("item['top_num']", type(item['top_num']))
            # yield item

            if item['detail_url']:
                yield scrapy.Request(
                    item['detail_url'],
                    meta={'item': item},
                    callback=self.parse_movie_detail
                    )
            # else:
            #     yield item

        self.start += 25
        while self.start <= 225:
            next_page = 'https://movie.douban.com/top250?start=' + str(self.start)
            yield scrapy.Request(next_page, callback=self.parse)


    def parse_movie_detail(self, response):
        item = DoubanMovieTop250Item()
        d = response.meta['item']
        movie_intro = response.xpath('//*[@id="link-report"]//span[@property="v:summary"]/text()')\
                            .extract_first()
        if movie_intro:
            movie_intro = movie_intro.strip()
        d['movie_intro'] = movie_intro
        item = d
        self.logger.error(item)
        yield item

