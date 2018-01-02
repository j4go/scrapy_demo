import pymongo
import MySQLdb
import traceback
import logging
import pickle
logger = logging.getLogger()


class RakutenPipeline:
    def process_item(self, item, spider):
        with open('rakuten.txt', 'a+', encoding='utf-8') as f:
            f.write(pickle.dumps(item)+'\n')


class DoubanPipeline(object):
    def process_item(self, item, spider):
        return item


class ImdbTopPipeline:
    def __init__(self):
        self.id = 1

    def process_item(self, item, spider):
        with open('imdb250.md', 'a+', encoding='utf-8') as f:
            title = item.get('title')
            score = item.get('score')
            count = item.get('count')
            f.write('|' + str(self.id) + '|' + title.split('/')[0] + '|'
                    + str(score) + '|' + str(count) + '|\n')
            self.id += 1
        return item


class DoubanFilePipeline:
    """写到文件"""
    def process_item(self, item, spider):
        with open('file.txt', 'a+', encoding='utf-8') as f:
            f.write(str(item) + '\n')


class DoubanMovieMySQLPipeline:
    '''存在则更新，不存在插入数据库'''

    def __init__(self, mysql_config):
        self.mysql_config = mysql_config

    @classmethod
    def from_crawler(cls, crawler):
        mysql_config = {
            'db': crawler.settings.get('MYSQL_DB'),
            'user': crawler.settings.get('MYSQL_USER'),
            'host': crawler.settings.get('MYSQL_HOST'),
            'passwd': crawler.settings.get('MYSQL_PASSWD'),
            'port': crawler.settings.get('MYSQL_PORT'),
            'charset': crawler.settings.get('MYSQL_CHARSET'),
        }
        return cls(mysql_config=mysql_config)

    def process_item(self, item, spider):
        con = MySQLdb.connect(**self.mysql_config)
        cur = con.cursor()
        logger.warning('连接打开')
        name = item['name']

        if name:
            logger.warning('处理电影：{}'.format(name))
            sql_fmt = """SELECT * from movie_detail where name='{}'"""
            select_sql = sql_fmt.format(name)
            try:
                cur.execute(select_sql)
                results = cur.fetchall()
                if results:  # 电影已经存在 更新
                    logger.warning('电影已经存在')
                    result = results[0]
                    res_dict = {  # 可能会变的值  注意 字段的顺序不能改变
                        'full_name': result[2],
                        'score': result[3],
                        'count': result[4],
                        'is_top250': result[5],
                        'top_num': result[6],
                        'detail_url': result[8],
                        'movie_intro': result[9],
                        'imdb': result[10],
                        'have_seen_count': result[11],
                        'want_see_count': result[12],
                        'short_comment_count': result[13],
                        'comment_count': result[14],
                    }
                    keys = res_dict.keys()
                    for k in keys:  # 检查每个key 会改变就update
                        if item[k] and res_dict[k] != item[k]:
                            logger.warning(
                                '{}字段有更新: {}'.format(k, item[k])
                                )
                            sql_fmt = """update movie_detail set
                                         {}='{}' where name = '{}'"""
                            update_sql = sql_fmt.format(k, item[k], name)
                            cur.execute(update_sql)

                else:  # 电影不存在，插入
                    logger.warning('电影不存在，存入数据库')
                    sql = """INSERT INTO movie_detail (
                            name, full_name, score, count, is_top250,
                            top_num, detail_url, movie_intro, imdb,
                            have_seen_count, want_see_count,
                            short_comment_count, comment_count
                            )
                            VALUES (
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s
                            )"""
                    args = (
                        item['name'], item['full_name'], item['score'],
                        item['count'], item['is_top250'], item['top_num'],
                        item['detail_url'], item['movie_intro'], item['imdb'],
                        item['have_seen_count'], item['want_see_count'],
                        item['short_comment_count'], item['comment_count']
                    )

                    cur.execute(sql, args)

            except Exception as e:
                logger.error(traceback.format_exc())
                con.rollback()
            else:
                con.commit()
            finally:
                cur.close()
                con.close()
                logger.warning('连接关闭')

        else:  # 电影名找不到 退出
            cur.close()
            con.close()
            logger.error('item中不存在电影名，跳过')
            logger.warning('连接关闭')


class DoubanMovieTop250MySQLPipeline:
    '''豆瓣Top250一次性写入Mysql表'''

    def __init__(self, mysql_config):
        self.values_list = []
        self.mysql_config = mysql_config

    @classmethod
    def from_crawler(cls, crawler):
        '''读取配置信息'''
        mysql_config = {
            'db': crawler.settings.get('MYSQL_DB'),
            'user': crawler.settings.get('MYSQL_USER'),
            'host': crawler.settings.get('MYSQL_HOST'),
            'passwd': crawler.settings.get('MYSQL_PASSWD'),
            'charset': crawler.settings.get('MYSQL_CHARSET'),
        }
        return cls(mysql_config=mysql_config)

    def process_item(self, item, spider):
        '''处理每个item'''
        values = (
            item["name"], item["full_name"], item["score"],
            item["count"], 1, item["top_num"], item["detail_url"],
            item["movie_intro"]
        )
        self.values_list.append(values)

    def close_spider(self, spider):
        '''处理完所有item关闭spider之前要做的处理'''
        con = MySQLdb.connect(**self.mysql_config)
        cur = con.cursor()
        logger.error('连接打开')
        sql = """REPLACE INTO movies (name, full_name, score, count,
                is_top250, top_num, detail_url, movie_intro)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
        try:
            cur.executemany(sql, self.values_list)
        except Exception as e:
            logger.error(traceback.format_exc())
            con.rollback()
        else:
            con.commit()
        finally:
            cur.close()
            con.close()
            logger.error('连接关闭')


class DoubanSubjectMongoPipeline:
    '''抓取的subject信息若存在则更新，不存在则插入数据库'''

    collection = 'subjects'

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DB')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        table = self.db[self.collection]
        subject_id = item.get('subject_id')  # 唯一 作为查找字段
        db_item = table.find_one({'subject_id': subject_id})
        if db_item:
            # id = db_item.get('_id')
            logger.warning('subject已经存在')
            for k, v in item.items():
                db_v = db_item.get(k)
                exclude_cols = ['subject_id', 'category']  # 不更新的keys列表
                if k not in exclude_cols and v and v != db_v:
                    logger.warning(
                        '更新字段{}：，原来的值：{}，更新为：{}'.format(k, db_v, v)
                        )
                    table.update({'subject_id': subject_id}, {'$set': {k: v}})
        else:
            logger.warning('subject不存在，存入数据库')
            table.insert_one(item)


class RakutenMongoPipeline:
    """抓取的subject信息若存在则更新，不存在则插入数据库"""

    collection = 'rakuten'

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DB')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        table = self.db[self.collection]

        item_url = item.get('item_url')  # 唯一 作为查找字段
        db_item = table.find_one({'item_url': item_url})
        if db_item:
            logger.warning('正在处理item_url：{}'.format(item_url))
            logger.warning('++++++++++++item_url已经存在++++++++++++++')
            for k, v in item.items():
                db_v = db_item.get(k)
                exclude_cols = ['item_url']  # 不更新的keys列表
                if k not in exclude_cols and v and v != db_v:
                    logger.warning(
                        '更新字段{}：，原来的值：{}，更新为：{}'.format(k, db_v, v)
                        )
                    table.update({'item_url': item_url}, {'$set': {k: v}})
        else:
            logger.warning('item不存在，存入数据库')
            table.insert_one(item)
