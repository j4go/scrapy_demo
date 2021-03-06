import urllib
import re
import json
from random import choice
from scrapy.spiders import Spider
from scrapy.http import FormRequest
from scrapy import Request
import time
import copy
from scrapy.selector import Selector

class Rakuten(Spider):

    def __init__(self):
        self.d = {}
        # self.with_com_item_count = {}
        self.url_list = [
            'https://review.rakuten.co.jp/item/1/332002_10005375/1.1/', # 测试评论
        ]

    name = 'rakuten_item_comment'

    def start_requests(self):
        self.logger.warning("rakuten start_requests请求入口")
        for url in self.url_list:
            yield Request(url,dont_filter=True,
                          meta={'cookiejar': 1},
                          callback=self.parse_comment_page,
                          )

    def parse_item_pages(self, response):
        url = response.url
        item = {}
        if '/204491/tg1004749/' in url:
            item['brand_name'] = '海尔'
        elif '/204491/tg1002881/' in url:
            item['brand_name'] = '东芝'
        elif '/204491/tg1004726/' in url:
            item['brand_name'] = '日立'
        elif '/204491/tg1002867/' in url:
            item['brand_name'] = '松下'
        elif '/204491/tg1002860/' in url:
            item['brand_name'] = '夏普'

        # 主URL搜索的商品条数
        total_num = 0
        total_num_str = '//h1[@class="section"]/text()[2]'
        total_num_result = response.xpath(total_num_str).re('[0-9]+')
        if total_num_result:
            total_num = int(total_num_result[0])
            item['total_items_num'] = total_num
        # 分页数 每页45条
        page_num = 0
        if total_num:
            page_num = total_num // 45
            if total_num % 45 != 0:
                page_num += 1
                item['total_items_page_num'] = page_num
        meta = {'cookiejar': response.meta['cookiejar'], 'item': item} # 传递item
        urls = [url] # 构造url列表
        p = 2
        while p <= page_num:
            urls.append(url + '?p=' + str(p))
            p += 1
        for url in urls:
            yield FormRequest.from_response(response, url=url, meta=meta, callback=self.parse_one_item_page)


    def parse_one_item_page(self, response):
        self.logger.warning('进入parse 处理一个商品列表分页')
        if response.status == 200:
            url = response.url
            d = copy.deepcopy(response.meta['item'])
            self.logger.warning('访问商品列表分页成功：{}'.format(url))
            total_num = d['total_items_num']
            page_num = d['total_items_page_num']
            # 当前分页所有有评论的链接
            with_com_links_str = '//a[@class="dui-rating-filter _link"]'
            with_com_links_result = response.xpath(with_com_links_str).extract()
            for with_com_item in with_com_links_result:
                item = copy.deepcopy(response.meta['item'])
                item['item_belong2_page_url'] =  url # 商品列表分页url
                find_link_reg = re.compile('href="(.*?)"')
                find_link_result = find_link_reg.findall(with_com_item)
                if find_link_result:
                    item['comment_url'] = find_link_result[0] # 评论详情页
                find_score_reg = re.compile('<span class="score">(.*?)</span>')
                find_score_result = find_score_reg.findall(with_com_item)
                if find_score_result:
                    item['avg_score'] = float(find_score_result[0]) # 平均评分
                find_score_num_reg = re.compile('<span class="legend">\((.*?)件\)</span>')
                find_score_num_result = find_score_num_reg.findall(with_com_item)
                if find_score_num_result:
                    item['score_people_count'] = int(find_score_num_result[0]) # 评论人数
                comment_page_count = 0  # 评论分页
                comment_page_count = item['score_people_count'] // 15
                if item['score_people_count'] % 15 != 0:
                    comment_page_count += 1
                item['comment_page_count'] = comment_page_count

                if item['comment_url']:
                    yield Request(item['comment_url'], dont_filter=True,
                                callback=self.parse_comment_page,
                                meta={'item': item, 'cookiejar': response.meta['cookiejar']}
                        )
        else:
            self.logger.error(response.url)
            self.logger.error('状态码为：{}'.format(response.status))



    def parse_comment_page(self, response):
        self.logger.warning('处理评论页面：{}'.format(response.url))

        # 处理单页信息 当前页
        coms_str = '//div[@class="revRvwUserMain"]'
        coms_results = response.xpath(coms_str).extract()

        # self.logger.warning('处理当前页的15条评论 开始')
        for coms_result in coms_results:
            self.logger.error(coms_result)
            # 处理单个评论
            single_com = {}
            # 用户评分
            user_score = 0
            user_score_reg = re.compile('<span class="revUserRvwerNum value">(.*?)</span>')
            user_score_result = user_score_reg.findall(coms_result)
            if user_score_result:
                user_score = int(user_score_result[0])
                single_com['user_score'] = user_score

            # 用户评论指标
            com_subjects_reg = re.compile('<li class="revUserDispList">(.*?):<span class="revDispListTxt">(.*?)</span></li>')
            com_subjects_result = com_subjects_reg.findall(coms_result)
            if com_subjects_result:
                td = {}
                for k, v in com_subjects_result:
                    td[k] = v
                single_com['com_subjects'] = td

            # 用户主评论
            com_summary_reg = re.compile('<dt class="revRvwUserEntryTtl summary">(.*?)</dt>')
            com_summary_result = com_summary_reg.findall(coms_result)
            if com_summary_result:
                single_com['com_summary'] = com_summary_result[0]

            # 用户评论详情

            # com_detail_reg = re.compile(r'<dd class="revRvwUserEntryCmt description">(\s+?)</dd>')
            # com_detail_result = com_detail_reg.findall(coms_result)
            # if com_detail_result:
            #     single_com['com_detail'] = com_detail_result[0]
            com_list = Selector(text=coms_result).xpath(
                '//dd[@class="revRvwUserEntryCmt description"]/text()').extract()
            single_com['com_detail'] = ''.join(com_list)
            self.logger.error(single_com['com_detail'])

            # 评论日期
            com_date_reg = re.compile('<span class="revUserEntryDate dtreviewed">(.*?)</span>')
            com_date_result = com_date_reg.findall(coms_result)
            if com_date_result:
                single_com['com_date'] = com_date_result[0]




















