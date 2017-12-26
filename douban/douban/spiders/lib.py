import traceback
import time
import re

def lib_parse_subject_detail(self, response):
    self.logger.warning("进入lib_parse_subject_detail处理")
    d = response.meta['item']
    detail_url = d['detail_url']

    # 没有subject_id 从url中截取subject_id
    if 'subject_id' not in d:
        subject_id = detail_url.split('/')
        if subject_id and len(subject_id) > 1:
            subject_id = subject_id[-2] # 倒数第2个
            d['subject_id'] = subject_id

    if response.status == 200:
        try:

            # 标题 subject名字
            name = ''
            name_str = '//span[@property="v:itemreviewed"]/text()'
            name = response.xpath(name_str).extract_first()
            d['name'] = name

            # subject年份
            year = 1900 # 给默认值
            year_str = '//span[@class="year"]/text()'
            year = response.xpath(year_str).re('[0-9]+')
            if year:
                year = int(year[0])
            d['year'] = year


            # subject别名 又名
            more_name = ''

            # more_name_str = '//*[@id="info"]/text()'
            # more_name = response.xpath(more_name_str).extract()
            # if more_name and len(more_name) > 17:
            #     # self.logger.error(len(more_name))
            #     more_name = more_name[16].strip()
            #     # self.logger.error(more_name)
            # else:
            #     more_name = ''

            more_name_str = '//div[@id="info"]'
            more_name_str_result = response.xpath(more_name_str).extract_first()
            re_str = re.compile('<span class="pl">又名:</span> (.*?)<br>')
            find_result = re_str.findall(more_name_str_result)
            if find_result:
                more_name = find_result[0]

            d['more_name'] = more_name
            if more_name:
                d['full_name'] = name + ' / ' + more_name
            else:
                d['full_name'] = name

            # subject评分
            score = 0
            score_str = '//*[@id="interest_sectl"]//*[@class="ll rating_num"]/text()'
            score = response.xpath(score_str).extract_first()
            if score:
                score = float(score)
            d['score'] = score


            # 评分人数
            count = 0  # 评分人数
            count_str = '//*[@class="rating_people"]/span[@property="v:votes"]/text()'
            count = response.xpath(count_str).extract_first()
            if count:
                count = int(count)
            d['count'] = count


            # subject简介
            movie_intro = ''
            intro_str = '//*[@id="link-report"]//span[@property="v:summary"]/text()'
            movie_intro = response.xpath(intro_str).extract_first()
            if movie_intro:
                movie_intro = movie_intro.strip().replace('"', '\"').replace("'", "\'")
            d['movie_intro'] = movie_intro


            # top250排名
            no = 0  # top250排名名次 默认为0
            top_no_str = '//*[@id="content"]//span[@class="top250-no"]/text()'
            # no_str = response.xpath(top_no_str).extract_first()
            # regex = re.compile('No.([0-9]*)')
            # find_result = regex.findall(no_str)
            # if find_result:
            #     no = int(find_result[0])

            # xpath + re替换掉上面的实现 对比下
            no_str = response.xpath(top_no_str).re('[0-9]+')
            if no_str:
                no = int(no_str[0])
            d['top_num'] = no
            if no:  # 是不是top250
                d['is_top250'] = 1
            else:
                d['is_top250'] = 0


            # imdb链接
            imdb = ''
            imdb_str = '//*[@id="info"]/a[starts-with(@href, "http://www.imdb.com/")]/text()'
            imdb = response.xpath(imdb_str).extract_first()
            if imdb:
                d['imdb'] = imdb
                d['imdb_url'] = 'http://www.imdb.com/title/' + imdb


            # 看过 and 想看
            have_seen_count = 0  # 有多少人标记看过
            want_see_count = 0  # 有多少人标记想看
            watching_count = 0  # 有多少人标记在看 电视剧才有
            interests_str = '//*[@id="subject-others-interests"]/div/a/text()'
            # interests = response.xpath(interests_str).extract()
            # if interests:
            #     regex = re.compile('^[0-9]*')
            #     have_seen_count = regex.findall(interests[0])
            #     if have_seen_count:
            #         have_seen_count = int(have_seen_count[0])
            #     want_see_count = regex.findall(interests[1])
            #     if want_see_count:
            #         want_see_count = int(want_see_count[0])

            # xpath + re替换掉上面的实现 对比下
            interests = response.xpath(interests_str).re('^[0-9]+')
            # 电影: 看过+想看   电视剧: 在看+看过+想看
            if len(interests):
                if len(interests) == 2:
                    have_seen_count = int(interests[0])
                    want_see_count = int(interests[1])
                elif len(interests) == 3:
                    watching_count = int(interests[0])
                    have_seen_count = int(interests[1])
                    want_see_count = int(interests[2])
                    d['watching_count'] = watching_count
            d['have_seen_count'] = have_seen_count
            d['want_see_count'] = want_see_count


            # 短评数量
            short_comment_count = 0  # 短评条数
            short_com_str = '//*[@id="comments-section"]/div/h2/span/a/text()'
            short_com = response.xpath(short_com_str).re('[0-9]+')
            if short_com:
                short_comment_count = int(short_com[0])
            d['short_comment_count'] = short_comment_count


            # 影评 长评数量
            comment_count = 0  # 影评条数
            com_str = '//*[@id="content"]//div/section/header/h2/span/a/text()'
            com = response.xpath(com_str).re('[0-9]+')
            if com:
                comment_count = int(com[0])
            d['comment_count'] = comment_count


            # 影片类型
            movie_type = []  # 影片类型
            type_str = '//*[@id="info"]/span[@property="v:genre"]/text()'
            type_str_result = response.xpath(type_str).extract()
            if type(type_str_result) == list:
                movie_type = type_str_result
            d['type'] = movie_type


            # 语言
            language = []
            language_str = '//div[@id="info"]'
            language_str_result = response.xpath(language_str).extract_first()
            re_str = re.compile('<span class="pl">语言:</span> (.*?)<br>')
            find_result = re_str.findall(language_str_result)
            if find_result:
                language = find_result[0]
                if '/' in language:
                    language = [s.strip() for s in language.split('/')]
                else:
                    language = [language]
            d['language'] = language


            # 单个视频长度 分钟
            runtime = 0
            runtime_str = '//span[@property="v:runtime"]/text()'
            runtime_str_result = response.xpath(runtime_str).re('[0-9]+')
            if runtime_str_result:
                runtime = int(runtime_str_result[0])
                d['runtime'] = runtime
            # 电视剧单集片长
            if d['category'] == '电视剧':
                runtime_str = '//div[@id="info"]'
                runtime_str_result = response.xpath(runtime_str).extract_first()
                re_str = re.compile('<span class="pl">单集片长:</span> (.*?)分钟<br>')
                find_result = re_str.findall(runtime_str_result)
                if find_result:
                    runtime = find_result[0]
                    re_str = re.compile('^[1-9]\d*')
                    find_result = re_str.findall(runtime)
                    if find_result:
                        runtime = int(find_result[0])
                        # self.logger.error(runtime)
            d['runtime'] = runtime


            videos_count = 0 # 电视剧 集数
            if d['category'] == '电视剧':
                videos_count_str = '//div[@id="info"]'
                videos_count_str_result = response.xpath(videos_count_str).extract_first()
                re_str = re.compile('<span class="pl">集数:</span> (.*?)<br>')
                find_result = re_str.findall(runtime_str_result)
                if find_result:
                    re_str = re.compile('^[1-9]\d*')
                    find_result = re_str.findall(find_result[0])
                    if find_result:
                        videos_count = int(find_result[0])
                        # self.logger.error(videos_count)
                    d['videos_count'] = videos_count


            # 导演
            director = []
            director_str = '//*[@rel="v:directedBy"]/text()'
            director_str_result = response.xpath(director_str).extract()
            if type(director_str_result) == list:
                director = director_str_result
            d['director'] = director


            # 主演
            actor = []
            actor_str = '//*[@rel="v:starring"]/text()'
            actor_str_result = response.xpath(actor_str).extract()
            if type(actor_str_result) == list:
                actor = actor_str_result
            d['actor'] = actor


            # 编剧
            scriptwriter = []
            scriptwriter_str = '//*[@id="info"]/span[2]/span[2]/a/text()'
            scriptwriter_str_result = response.xpath(scriptwriter_str).extract()
            if type(scriptwriter_str_result) == list:
                scriptwriter = scriptwriter_str_result
            d['scriptwriter'] = scriptwriter


            # 制片国家地区
            region = []
            region_str = '//div[@id="info"]'
            region_str_result = response.xpath(region_str).extract_first()
            re_str = re.compile('<span class="pl">制片国家/地区:</span> (.*?)<br>')
            find_result = re_str.findall(region_str_result)
            if find_result:
                region = find_result[0]
                if '/' in region:
                    region = [r.strip() for r in region.split('/')]
                else:
                    region = [region]
            d['region'] = region

            d['update_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())


            self.logger.warning(d)

            yield d

        except Exception as e:
            self.logger.error(traceback.format_exc())
    else:
        self.logger.error('++++++++++++++++出错了，内容如下:')
        self.logger.error(response.url)
        self.logger.error('lib_parse_subject_detail 状态码为：{}'.format(response.status))
        self.logger.error('++++++++++++++++')

