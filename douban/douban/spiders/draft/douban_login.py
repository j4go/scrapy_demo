import scrapy
import urllib
import re
import time
from scrapy.http import FormRequest


class DoubanLogin(scrapy.Spider):

    name = 'douban_login'

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            username = crawler.settings.get('DOUBAN_USERNAME'),
            nickname = crawler.settings.get('DOUBAN_NICKNAME'),
            password = crawler.settings.get('DOUBAN_PASSWORD')
        )

    def start_requests(self):
        login_url = 'https://www.douban.com/accounts/login'
        return [scrapy.Request(login_url, meta={'cookiejar': 1}, callback=self.post_login)]

    def post_login(self, response):
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
        url = 'https://movie.douban.com/'
        req = scrapy.Request(url, meta={'cookiejar': response.meta['cookiejar']})
        yield req


    def parse(self, response):
        unicode_body = response.body_as_unicode()
        if self.nickname in unicode_body:
            self.logger.warning("登录成功")
        else:
            self.logger.warning("登录失败")




    # def _requests_to_follow(self, response):
    #         if not isinstance(response, HtmlResponse):
    #             return
    #         seen = set()
    #         for n, rule in enumerate(self._rules):
    #             links = [l for l in rule.link_extractor.extract_links(response) if l not in seen]
    #             if links and rule.process_links:
    #                 links = rule.process_links(links)
    #             for link in links:
    #                 seen.add(link)
    #                 r = Request(url=link.url, callback=self._response_downloaded)
    #                 # 下面这句是重写的
    #                 r.meta.update(rule=n, link_text=link.text, cookiejar=response.meta['cookiejar'])
    #                 yield rule.process_request(r)
