# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import scrapy
from pymongo import MongoClient
from scrapy.pipelines.images import ImagesPipeline


class CastoramaparserPipeline:

    def __init__(self):
        client = MongoClient('127.0.0.1', 27017)
        self.mongo_base = client.castorama

    def process_item(self, item, spider):
        collection = self.mongo_base[spider.name]
        item_from_db = collection.find_one({'_id': item['_id']})
        has_item = bool(item_from_db)
        if not has_item:
            collection.insert_one(item)

        return item


class CastoramaPhotosPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['photos']:
            for img in item['photos']:
                try:
                    yield scrapy.Request(img)
                except Exception as err:
                    print(err)

    def item_completed(self, results, item, info):
        item['photos'] = [item[1] for item in results if item[0]]
        return item

    def file_path(self, request, response=None, info=None, *, item=None):
        filename = request.url.split('/')[-1]
        return f'full/{item["_id"]}/{filename}'
