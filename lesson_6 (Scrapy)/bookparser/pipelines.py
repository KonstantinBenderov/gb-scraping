# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient


class BookparserPipeline:

    def __init__(self):
        client = MongoClient('127.0.0.1', 27017)
        self.mongo_base = client.labirint

    def process_item(self, item, spider):
        return item
