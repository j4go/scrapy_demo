import urllib
import re
import json
from random import choice
from scrapy.spiders import Spider
from scrapy.http import FormRequest
from scrapy import Request
import time

from .lib import  lib_parse_subject_detail

class Rakuten(Spider):

    def __init__(self):
        self.ids = set()
        self.url_list = [
            'https://search.rakuten.co.jp/search/mall/-/204491/tg1004749/', # 海尔
        ]

    name = 'rakuten_item'

    def start_requests(self):
        self.logger.warning("rakuten start_requests请求入口")
        for url in self.url_list:
            yield Request(url,
                          meta={'cookiejar': 1},
                          callback=self.with_cookie,
                          dont_filter=True)

    def with_cookie(self, response):
        url = response.url
        item = {}
        # 主URL搜索的商品条数
        total_num = 0
        total_num_str = '//h1[@class="section"]/text()[2]'
        total_num_result = response.xpath(total_num_str).re('[0-9]+')
        if total_num_result:
            total_num = int(total_num_result[0])
            item['total_num'] = total_num

        # 分页数 每页45条
        page_num = 0
        if total_num:
            page_num = total_num // 45
            if total_num % 45 != 0:
                page_num += 1
                item['page_num'] = page_num

        meta = {'cookiejar': response.meta['cookiejar'], 'item': item}

        urls = [url] # 构造url列表
        p = 2

        while p <= page_num:
            urls.append(url + '?p=' + str(p))
            p += 1
        self.logger.error(urls)
        for url in urls:
            yield FormRequest.from_response(response,
                                              url=url,
                                              meta=meta,
                                              callback=self.parse)
    # def test(self, response):
    #     self.logger.warning(response.request.headers)

    # def deal_first_page(self, response):
    #     # self.logger.warning(response.request.headers)
    #     url = response.url
    #     item = {}
    #     # 主URL搜索的商品条数
    #     total_num = 0
    #     total_num_str = '//h1[@class="section"]/text()[2]'
    #     total_num_result = response.xpath(total_num_str).re('[0-9]+')
    #     if total_num_result:
    #         total_num = int(total_num_result[0])
    #         item['total_num'] = total_num
    #
    #     # 分页数 每页45条
    #     page_num = 0
    #     if total_num:
    #         page_num = total_num // 45
    #         if total_num % 45 != 0:
    #             page_num += 1
    #             item['page_num'] = page_num
    #
    #     meta = {'cookiejar': response.meta['cookiejar'], 'item': item}
    #
    #     yield Request(url,
    #                   callback=self.parse,
    #                   dont_filter=True,
    #                   meta=meta,
    #                   cookies=c,
    #                   headers=headers
    #                   )
    #
    #     # urls = [url] # 构造url列表
    #     p = 2
    #     while p <= page_num:
    #         # urls.append(url + 'p=' + str(p))
    #         headers['referer'] = url
    #         url += 'p=' + str(p)
    #         p += 1
    #         yield Request(url,
    #                       callback=self.parse,
    #                       dont_filter=True,
    #                       meta=meta,
    #                       cookies=c,
    #                       headers=headers
    #                       )

        # self.logger.error(urls)
        #
        # for url in urls:
        #     meta = {'cookiejar': response.meta['cookiejar'], 'item': item}
        #     yield Request(url,
        #                   callback=self.parse,
        #                   dont_filter=True,
        #                   meta=meta,
        #                   cookies=c
        #                   )


    # def deal_each_page(self, response):
    #     self.logger.warning("rakuten deal_each_page请求入口")
    #     url = response.url
    #     item = {}
    #     # 主URL搜索的商品条数
    #     total_num = 0
    #     total_num_str = '//h1[@class="section"]/text()[2]'
    #     total_num_result = response.xpath(total_num_str).re('[0-9]+')
    #     if total_num_result:
    #         total_num = int(total_num_result[0])
    #         item['total_num'] = total_num
    #
    #     # 分页数 每页45条
    #     page_num = 0
    #     if total_num:
    #         page_num = total_num // 45
    #         if total_num % 45 != 0:
    #             page_num += 1
    #             item['page_num'] = page_num
    #     self.logger.warning(response.request.headers)
    #     yield Request(
    #             url,
    #             callback=self.parse,
    #             meta={'cookiejar': response.meta['cookiejar'], 'item': item},
    #             dont_filter=True
    #     )
    #
    #     if 'p=' not in url:
    #         url += 'p=1'
    #
    #     p = int(url.split('=')[-1])  # 当前页数
    #
    #     self.logger.warning('当前页和总页数')
    #     self.logger.warning(p)
    #     self.logger.warning(page_num)
    #
    #     while p < page_num:
    #         # time.sleep(3)
    #         p += 1
    #         url = url.split('=')
    #         url[-1] = str(p)
    #         url = '='.join(url)
    #         self.logger.warning(url)
    #         self.logger.warning('当前页和总页数')
    #         self.logger.warning(p)
    #         self.logger.warning(page_num)
    #         self.logger.warning(response.request.headers)
    #         yield Request(
    #                 url,
    #                 callback=self.parse,
    #                 meta={'cookiejar': response.meta['cookiejar'], 'item': item},
    #                 dont_filter=True
    #         )


    def parse(self, response):
        self.logger.warning('进入parse')
        if response.status == 200:
            url = response.url
            self.logger.warning('访问分页URL成功：{}'.format(url))
            total_num = response.meta['item']['total_num']
            page_num = response.meta['item']['page_num']
            tmp_item = {}
            if '/204491/tg1004749/' in url:
                tmp_item['brand_name'] = '海尔'

            # 商品名称
            item_title_str = '//div[@class="content title"]/h2/a/text()'
            item_title_result = response.xpath(item_title_str).extract_first()
            if item_title_result:
                tmp_item['item_title'] = item_title_result.replace(u'\u3000', u'')
                # self.logger.warning(item_title_result)

            # 商品主页
            item_str = '//div[@class="content title"]/h2'
            item_result = response.xpath(item_str).extract_first()
            if item_result:
                find_href = re.compile('href="(.*?)"')
                find_result = find_href.findall(item_result)
                if find_result:
                    find_result = find_result[0]
                    tmp_item['item_url'] = find_result
                    tmp_item['item_id'] = find_result.split('/')[-2]
                    self.ids.add(tmp_item['item_id'])
                    self.logger.error('正在处理商品item_id:')
                    self.logger.error(tmp_item['item_id'])
                    self.logger.error(self.ids)

                    # self.logger.warning(item_result)

            # 当前分页所有有评论的链接
            with_com_links_str = '//a[@class="dui-rating-filter _link"]'
            with_com_links_result = response.xpath(with_com_links_str).extract()

            for with_com_item in with_com_links_result:
                item = {'category_url': url} # 大分类url
                item.update(tmp_item)
                find_link_reg = re.compile('href="(.*?)"')
                find_link_result = find_link_reg.findall(with_com_item)
                if find_link_result:
                    item['comment_url'] = find_link_result[0] # 评论详情页
                    # self.logger.error(find_link_result[0])
                find_score_reg = re.compile('<span class="score">(.*?)</span>')
                find_score_result = find_score_reg.findall(with_com_item)
                if find_score_result:
                    item['avg_score'] = float(find_score_result[0]) # 平均评分
                    # self.logger.error(find_score_result[0])
                find_score_num_reg = re.compile('<span class="legend">\((.*?)件\)</span>')
                find_score_num_result = find_score_num_reg.findall(with_com_item)
                if find_score_num_result:
                    item['score_num'] = int(find_score_num_result[0]) # 评论人数
                    # self.logger.error(find_score_num_result[0])
                # self.logger.error(item)
                comment_page_num = 0  # 评论分页
                comment_page_num = item['score_num'] // 15
                if item['score_num'] % 15 != 0:
                    comment_page_num += 1
                item['comment_page_num'] = comment_page_num

                # self.logger.error(item)

                if item['comment_url']:
                    yield Request(
                            item['comment_url'],
                            callback=self.parse_comment_detail,
                            meta={'item': item, 'cookiejar': response.meta['cookiejar']},
                            dont_filter=True
                    )

        else:
            self.logger.error(response.url)
            self.logger.error('状态码为：{}'.format(response.status))



    def parse_comment_detail(self, response):
        self.logger.warning('处理评论页面：{}'.format(response.url))
        d = response.meta['item']
        # self.logger.error(d)

        url = response.url

        p = int(url.split('/')[-2].split('.')[0])  # 当前页数
        page_num = d['comment_page_num']


        if 'comment_list' not in d:
            d['comment_list'] = []  # 元素是dict 存放所有的评论信息
        # if 'comment_list' in self.d:
        #     d['comment_list'] = self.d.get('comment_list')
        # else:
        #     d['comment_list'] = []

        # 处理单页 当前页
        coms_str = '//div[@class="revRvwUserMain"]'
        coms_results = response.xpath(coms_str).extract()

        self.logger.warning('处理当前页的15条评论 开始')

        for coms_result in coms_results:
            # 处理单个评论
            single_com = {}

            # 用户评分
            user_score = 0
            user_score_reg = re.compile('<span class="revUserRvwerNum value">(.*?)</span>')
            user_score_result = user_score_reg.findall(coms_result)
            if user_score_result:
                user_score = int(user_score_result[0])
                single_com['user_score'] = user_score
                # self.logger.error(user_score_result)

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
            com_detail_reg = re.compile('<dd class="revRvwUserEntryCmt description">(.*?)</dd>')
            com_detail_result = com_detail_reg.findall(coms_result)
            if com_detail_result:
                # self.logger.error(com_detail_result)
                single_com['com_detail'] = com_detail_result[0]

            # 评论日期
            com_date_reg = re.compile('<span class="revUserEntryDate dtreviewed">(.*?)</span>')
            com_date_result = com_date_reg.findall(coms_result)
            if com_date_result:
                # self.logger.error(com_detail_result)
                single_com['com_date'] = com_date_result[0]

            if single_com not in d['comment_list']:
                d['comment_list'].append(single_com)
                # self.d['comment_list'] = d['comment_list']

            # yield d

        # d = response.meta['item']
        self.logger.warning('处理当前页的15条评论 结束')
        self.logger.warning('处理下一页')
        # 处理评论分页
        # url = response.url  # 当前的url
        # page_num = d['comment_page_num']
        # # self.logger.warning(page_num)
        # p = int(url.split('/')[-2].split('.')[0])  # 当前页数
        # self.logger.warning(p)
        if p < page_num:
            # p += 1
            url = url.split('/')
            url[-2] = str(p) + '.1'
            url = '/'.join(url)
            self.logger.warning('处理评论分页：{}'.format(url))
            yield Request(
                    url,
                    callback=self.parse_comment_detail,
                    meta={'item': d, 'cookiejar': response.meta['cookiejar']}
            )
        elif p == page_num:
            self.logger.error('处理完一个商品的评论+++++++++++++++++++++++++++++++')
            self.logger.error(len(d['comment_list']))
            self.logger.error('处理完一个商品的评论———————————————————————————————')
            yield d

















