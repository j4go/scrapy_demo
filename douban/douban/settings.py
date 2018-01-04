# Scrapy settings for douban project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
# http://doc.scrapy.org/en/latest/topics/settings.html
# http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
# http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html

import os
import json
import traceback

# 自定义的配置文件路径
file_dir = '/data/config/mysql.json'
mysql_config = {}
try:
    with open(file_dir, 'r') as json_file:
        mysql_config = json.load(json_file)
except Exception as e:
    print('读取自定义配置出错')
    print(traceback.format_exc())

BOT_NAME = 'douban'

SPIDER_MODULES = ['douban.spiders']
NEWSPIDER_MODULE = 'douban.spiders'


# Crawl responsibly by identifying
# yourself (and your website) on the user-agent
# USER_AGENT = 'douban (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False
# COOKIES_ENABLED = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
# CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
# DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = True

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
  'Accept-Language': 'en',
  'User-Agent': ('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; '
                 'AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)')
}


# Enable or disable spider middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#     'douban.middlewares.DoubanSpiderMiddleware': 543,
# }

# Enable or disable downloader middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
# DOWNLOADER_MIDDLEWARES = {
#    'douban.middlewares.MyCustomDownloaderMiddleware': 543,
# }

# Enable or disable extensions
# See http://scrapy.readthedocs.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
# }

# Configure item pipelines
# See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html
# ITEM_PIPELINES = {
#    'douban.pipelines.DoubanPipeline': 300,
# }

# Enable and configure the AutoThrottle extension (disabled by default)
# See http://doc.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = 'httpcache'
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

# 抓取速度 单位秒
DOWNLOAD_DELAY = 3

CONCURRENT_REQUESTS_PER_DOMAIN = 1  # default 8

DOWNLOAD_TIMEOUT = 60  # default 180

DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddleware.useragent.UserAgentMiddleware': None,
    # 'douban.middlewares.IPPOOLS': 300,
    # 'douban.middlewares.IPProxy': 300,
    'douban.middlewares.MyUserAgentMiddleware': 400,
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': 500,
}

RETRY_ENABLED = True
RETRY_TIMES = 100
RETRY_HTTP_CODES = [500, 503, 504, 400, 408]
RETRY_PRIORITY_ADJUST = -1

ITEM_PIPELINES = {
    # 'douban.pipelines.DoubanMovieMySQLPipeline': 300,  # 写入mysql
    'douban.pipelines.DoubanSubjectMongoPipeline': 400,  # 写入mongodb
    # 'douban.pipelines.DoubanFilePipeline': 300,  # 写入文件
    # 'douban.pipelines.RakutenPipeline': 300,  # 写入文件
    # 'douban.pipelines.RakutenMongoPipeline': 300,
}


MYSQL_HOST = '127.0.0.1'
MYSQL_DB = 'douban'
MYSQL_USER = mysql_config.get('user')
MYSQL_PASSWD = mysql_config.get('password')
MYSQL_PORT = mysql_config.get('port')
MYSQL_CHARSET = 'utf8'

MONGO_URI = 'mongodb://localhost:27017'
MONGO_DB = "douban"

CSDN_USERNAME = mysql_config.get('csdn_username')
CSDN_PASSWORD = mysql_config.get('csdn_password')

DOUBAN_USERNAME = mysql_config.get('douban_username')
DOUBAN_NICKNAME = mysql_config.get('douban_nickname')
DOUBAN_PASSWORD = mysql_config.get('douban_password')

# 默认处理200-300的状态码  指定要处理的状态码 不然会跳过
HTTPERROR_ALLOWED_CODES = [404, 403, 401, 500, 503, 504, 505]

# 指定日志文件 不指定则会在控制台上输出
# LOG_FILE = '/data/logs/scrapy.log'
LOG_LEVEL = 'DEBUG'

# 设置IP池 210.13.50.103:3128
IPPOOL = [
    {'ipaddr': '123.14.175.175:8118'},
]

PROXY = "http://1b2983d3368f5af8:d68183588598522c@dongtai.xieyaoyun.com:33002"

# 从文件读取user_agent
file_path = os.path.join(os.path.dirname(__file__), 'user_agent.txt')
MY_USER_AGENT = [line.strip('\n') for line in open(file_path)]

if __name__ == '__main__':
    print(MY_USER_AGENT)
