import scrapy
import urllib
import re
import time
from random import choice
from scrapy.spiders import Spider
from scrapy.http import FormRequest
from douban.items import DoubanMovieTop250Item


class DoubanLoginInfo(Spider):

    def __init__(self, username, nickname, password):
        self.top_num = 0
        self.username = username
        self.nickname = nickname
        self.password = password

    name = 'douban_get_info_login'

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            username = crawler.settings.get('DOUBAN_USERNAME'),
            nickname = crawler.settings.get('DOUBAN_NICKNAME'),
            password = crawler.settings.get('DOUBAN_PASSWORD')
        )

    def start_requests(self):
        self.logger.warning("start_request 请求入口")
        login_url = 'https://www.douban.com/accounts/login'
        return [scrapy.Request(login_url, meta={'cookiejar': 1}, callback=self.post_login)]

    def post_login(self, response):
        self.logger.warning("提交参数模拟登录")
        html = urllib.request.urlopen(response.url).read().decode('utf-8')
        # 验证码图片地址
        search_str = '<img id="captcha_image" src="(.+?)" alt="captcha" class="captcha_image"/>'
        imgurl = re.search(search_str, html)
        if imgurl:
            url = imgurl.group(1)
            # 将图片保存至同目录下
            res = urllib.request.urlretrieve(url, 'v.jpg')
            # 获取captcha-id参数
            search_str2 = '<input type="hidden" name="captcha-id" value="(.+?)"/>'
            captcha = re.search(search_str2, html)
            if captcha:
                vcode = input('请输入图片上的验证码：')
                return [FormRequest.from_response(response,
                          meta={'cookiejar': response.meta['cookiejar']},
                          formdata={
                              'source': 'index_nav',
                              'form_email': self.username,
                              'form_password': self.password,
                              'captcha-solution': vcode,
                              'captcha-id': captcha.group(1)
                          },
                          callback=self.after_login,
                          dont_filter=True)
                        ]
        return [FormRequest.from_response(response,
                  meta={'cookiejar': response.meta['cookiejar']},
                  formdata={
                      'source': 'index_nav',
                      'form_email': self.username,
                      'form_password': self.password
                  },
                  callback=self.after_login,
                  dont_filter=True)
                ]


    def after_login(self, response):
        self.logger.warning("模拟登录结束")
        urls = ['https://movie.douban.com/top250?start=' + str(i)
                    for i in range(250) if i % 25 == 0]
        for url in urls:
            time.sleep(1)
            yield scrapy.Request(url, meta={'cookiejar': response.meta['cookiejar']})


    def parse(self, response):
        self.logger.warning("进入parse处理")

        # unicode_body = response.body_as_unicode()
        # if self.nickname in unicode_body:
        #     self.logger.warning("模拟登录成功")
        # else:
        #     self.logger.warning("模拟登录失败")

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
            item['count'] = int(count_str)
            self.top_num += 1
            item['top_num'] = self.top_num
            time.sleep(choice(range(3)))
            yield scrapy.Request(
                item['detail_url'],
                callback=self.parse_movie_detail,
                meta={'item': item, 'cookiejar': response.meta['cookiejar']},
                dont_filter=True
            )


    def parse_movie_detail(self, response):
        self.logger.warning("进入parse_movie_detail处理")
        item = DoubanMovieTop250Item()
        d = response.meta['item']

        movie_intro = ''
        if response.status == 200:
            x_str = '//*[@id="link-report"]//span[@property="v:summary"]/text()'
            movie_intro = response.xpath(x_str).extract_first()
            if movie_intro:
                movie_intro = movie_intro.strip().replace('"', '\"').replace("'", "\'")
        else:
            self.logger.error(response.url)
            self.logger.error('parse_movie_detail 状态码为：{}'.format(response.status))

        d['movie_intro'] = movie_intro
        item = d
        self.logger.warning(item)
        yield item



