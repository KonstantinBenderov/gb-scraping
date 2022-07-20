# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BookparserItem(scrapy.Item):
    _id = scrapy.Field()
    author = scrapy.Field()
    title = scrapy.Field()
    price_old = scrapy.Field()
    price_new = scrapy.Field()
    url = scrapy.Field()
