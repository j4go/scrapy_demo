import scrapy
import re
from scrapy.http import FormRequest

class Csdn(scrapy.Spider):

    def __init__(self):
        t1 = None
        t2 = None

    name = "csdn"


    header = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0'}

    # start_urls = (
    #     'https://passport.csdn.net/account/login?from=http://www.csdn.net',
    # )

    # cookie = "uuid_tt_dd=10_36582888400-1512550040425-895420; UserName=celavie1205; UserInfo=NNW2KrfykonLM4hT%2BQm%2BWsV%2F9Q8YjSyMsqy0EIUSDkdfCcxOrnGlriID%2BrMOG8txFIMAxQSUxekXxL89ICC%2Bse7y6LeYDkTVzVfhglpYAT9qjE%2FA1kRJRfWj8HP0TWdjiQrV33ckl3kFalpuyk7hlw%3D%3D; UserNick=celavie1205; AU=DE4; UN=celavie1205; UE="linguifan2010@yahoo.cn"; BT=1512550039224; access-token=235794db-14af-45ac-b49e-0ecb0fda16a4; dc_tos=p0j72y; dc_session_id=10_1512550040425.399662; Hm_lvt_6bcd52f51e9b3dce32bec4a3997715ac=1512468555,1512471627,1512472693,1512543616; Hm_lpvt_6bcd52f51e9b3dce32bec4a3997715ac=1512550043"


    # Start on the welcome page
    def start_requests(self):
        # https://passport.csdn.net/account/login?from=http://my.csdn.net/my/mycsdn
        # https://passport.csdn.net/account/login?from=http://www.csdn.net
        return [
            scrapy.Request( "https://passport.csdn.net/account/login?from=http://www.csdn.net",
                callback=self.parse_login, meta={'cookiejar':1})
        ]

    # Post welcome page's first form with the given user/pass
    # def parse(self, response):
    #     # 请求Cookie
    #     Cookie3 = response.request.headers.getlist('Cookie')
    #     print('登录后再次请求：',Cookie3)
    #     # with open('csdn_logined_index.html', 'wb') as f:
    #     #     f.write(response.body)
    #     body = response.body  # 获取网页内容字节类型
    #     unicode_body = response.body_as_unicode()  # 获取网站内容字符串类型
    #     # print(unicode_body)
    #     if 'celavie1205' in str(unicode_body):
    #         self.log("You've logined in!!!")
    #     # yield response
    #     # r = response.xpath('//*[@id="showinfo"]/a[@href="http://my.csdn.net/"]\
    #     #     /em/text()').extract_first()
    #     # self.logger.error('RESPONSE:' + str(r))


    def parse_login(self, response):
        # r = response.xpath('//*[@id="showinfo"]/a[@href="http://my.csdn.net/"]\
        #     /em/text()').extract_first()
        # self.logger.error('RESPONSE:' + str(r))
        # 响应Cookie
        # Cookie1 = response.headers.getlist('Set-Cookie')
        #查看一下响应Cookie，也就是第一次访问注册页面时后台写入浏览器的Cookie
        # print(Cookie1)
        self.log('带着data去验证用户名和密码')
        data = {'username': 'celavie1205', 'password': 'celavie964760'}
        res = response.xpath('//*[@id="fm1"]/input[@type="hidden"]').extract()
        for r in res:
            r_list = r.split('"')
            data[str(r_list[3])] = r_list[5]
            # self.log(r_list[3])
            # self.log(r_list[5])
            self.log(data)
        # self.log("---------------------------------------")
        return [FormRequest.from_response(response,
                    url="https://passport.csdn.net/account/verify",
                    formdata=data,
                    meta={'cookiejar':response.meta['cookiejar']},
                    callback=self.after_post)]

    def after_post(self, response):
        Cookie3 = response.request.headers.getlist('Cookie')
        print(response.request.headers)
        print('访问首页前前前前前前前前前前前前前前前的cookie：', Cookie3)
        # response.request.headers.Referer = 'https://passport.csdn.net/account/verify;jsessionid=701352F4DCD4C61DB887EC99545A376A.tomcat2'
        # response.request.headers
        self.log("+++++++++++++++++++++++++++++++++++++++")
        self.log("post后带着cookie访问首页")
        self.log("+++++++++++++++++++++++++++++++++++++++")
        return [
            scrapy.Request("https://www.csdn.net",
                callback=self.parse_index, meta={'cookiejar':1})
        ]



    def parse_index(self, response):
        Cookie3 = response.request.headers.getlist('Cookie')[0].decode('utf-8')
        cookies = Cookie3.split(';')
        print(type(cookies))
        c = {}
        for cookie in cookies:
            arr = cookie.split('=')
            c[arr[0].strip()] = arr[1]
        print(c)
        print('访问首页时时时时时时时时时时时时时时时时的cookie：', c)

        print(response.request.headers)
        self.t1 = Cookie3

        # headers = {
        #     'Connection': 'keep - alive',  # 保持链接状态
        #     'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36'
        # }

        return [
            scrapy.Request("http://download.csdn.net/",
                callback=self.parse_blog,
                # headers=headers,
                cookies=c,
                )
        ]

    def parse_blog(self, response):
        # self.log("访问csdn博客")
        Cookie3 = response.request.headers.getlist('Cookie')
        print(response.request.headers)
        print('访问csdn博客时的cookie：', Cookie3)
        self.t2 = Cookie3
        if self.t1 == self.t2:
            self.log("))))))))))))))))))))))))))))))))))))))))))))))))))))))))")
        unicode_body = response.body_as_unicode()  # 获取网站内容字符串类型
        if 'celavie1205' in unicode_body:
            self.log("登录成功")
        elif '登录' in unicode_body:
            self.log("登录失败！")
        # else:
        #     self.log(unicode_body)

