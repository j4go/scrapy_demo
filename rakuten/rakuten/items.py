# Define here the models for your scraped items
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class RakutenItem(Item):
    name = Field()
    year = Field()


class RakutenTopItem(Item):
    title = Field()
    score = Field()
    count = Field()


class ImdbTopItem(Item):
    title = Field()
    score = Field()
    count = Field()


class RakutenMovieTop250Item(Item):
    name = Field()
    full_name = Field()
    score = Field()
    count = Field()
    top_num = Field()
    detail_url = Field()
    movie_intro = Field()
