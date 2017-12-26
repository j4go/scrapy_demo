import scrapy
import re
from scrapy.http import FormRequest

class Csdn(scrapy.Spider):

    name = "csdn2"

    # Start on the welcome page
    def start_requests(self):
        return [
            scrapy.Request( "https://passport.csdn.net/account/login?from=http://www.csdn.net",
                callback=self.parse_login, meta={'cookiejar':1})
        ]

    # Post welcome page's first form with the given user/pass
    def parse(self, response):
        # 请求Cookie
        Cookie3 = response.request.headers.getlist('Cookie')
        print('查看需要登录才可以访问的页面携带Cookies：',Cookie3)
        with open('csdn_logined_index.html', 'wb') as f:
            f.write(response.body)
        # if 'celavie1205' in str(response.body):
        #     self.log("You've logined in!!!")


    def parse_login(self, response):
        # r = response.xpath('//*[@id="showinfo"]/a[@href="http://my.csdn.net/"]\
        #     /em/text()').extract_first()
        # self.logger.error('RESPONSE:' + str(r))
        # 响应Cookie
        Cookie1 = response.headers.getlist('Set-Cookie')
        #查看一下响应Cookie，也就是第一次访问注册页面时后台写入浏览器的Cookie
        print(Cookie1)
        print('登录中')
        data = {'username': 'celavie1205', 'password': 'celavie964760'}
        res = response.xpath('//*[@id="fm1"]/input[@type="hidden"]').extract()
        for r in res:
            r_list = r.split('"')
            data[str(r_list[3])] = r_list[5]
            self.log(r_list[3])
            self.log(r_list[5])
            self.log(data)
        self.log("---------------------------------------")
        return [FormRequest(url="https://passport.csdn.net/account/verify",
                    formdata=data,
                    meta={'cookiejar':response.meta['cookiejar']},
                    callback=self.after_post)]

    def after_post(self, response):
        self.log(response.url)
        Cookie2 = response.request.headers.getlist('Cookie')
        print(Cookie2)
        self.log("+++++++++++++++++++++++++++++++++++++++")
        return [
            scrapy.Request("http://www.csdn.net",
                callback=self.parse, meta={'cookiejar':response.meta['cookiejar']},)
        ]


