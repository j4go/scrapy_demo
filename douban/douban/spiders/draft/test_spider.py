import scrapy
import re


class Test(scrapy.Spider):

    name = "test"

    start_urls = (
        'https://www.csdn.net/',
    )

    def parse(self, response):
        r = response.xpath('//*[@id="showinfo"]/a[@href="http://my.csdn.net/"]\
            /em/text()').extract_first()
        self.logger.error('RESPONSE:' + str(r))
