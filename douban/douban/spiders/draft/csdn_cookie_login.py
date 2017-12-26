import scrapy
from scrapy.http import FormRequest

class Csdn(scrapy.Spider):

    name = 'csdn_cookie_login'

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            username = crawler.settings.get('CSDN_USERNAME'),
            password = crawler.settings.get('CSDN_PASSWORD')
        )

    def start_requests(self):
        return [
            scrapy.Request('https://passport.csdn.net/account/login',
             callback=self.parse_login, meta={'cookiejar':1})
        ]

    def parse_login(self, response):
        data = {'username': self.username, 'password': self.password}
        res = response.xpath('//*[@id="fm1"]/input[@type="hidden"]').extract()
        for r in res:
            r_list = r.split('"')
            data[str(r_list[3])] = r_list[5]
        return [FormRequest.from_response(response,
                    url="https://passport.csdn.net/account/verify",
                    formdata=data,
                    meta={'cookiejar':response.meta['cookiejar']},
                    callback=self.after_post)]

    def after_post(self, response):
        return [
            scrapy.Request("https://www.csdn.net",
                callback=self.parse_index, meta={'cookiejar':1})
        ]

    def parse_index(self, response):
        cookies = response.request.headers.getlist('Cookie')[0].decode('utf-8')
        cookies = cookies.split(';')
        cookies_dict = {}
        for cookie in cookies:
            arr = cookie.split('=')
            cookies_dict[arr[0].strip()] = arr[1]

        # http://download.csdn.net/ 可以登录
        # http://huiyi.csdn.net/ 可以登录
        # http://geek.csdn.net/ 可以登录
        return [
            scrapy.Request("http://my.csdn.net/",
                callback=self.parse_blog,
                cookies=cookies_dict,
                )
        ]

    def parse_blog(self, response):
        self.logger.warning("parse_blog")
        unicode_body = response.body_as_unicode()
        if self.username in unicode_body:
            self.logger.warning("登录成功")
        elif '登录' in unicode_body:
            self.logger.warning("登录失败！")
        else:
            self.logger.warning("其他情况")
        res = response.xpath('//a[@href="/my/follow"][1]/text()').extract_first()
        self.logger.warning('我关注的人数：' + res)

