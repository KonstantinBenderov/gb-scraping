import scrapy
from scrapy.http import HtmlResponse
from scrapy.loader import ItemLoader

from castoramaparser.items import CastoramaparserItem


class CastoramaruSpider(scrapy.Spider):
    name = 'castoramaru'
    allowed_domains = ['castorama.ru']

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.start_urls = [f'https://www.castorama.ru/catalogsearch/result/?q={kwargs.get("search")}']

    def parse(self, response: HtmlResponse):
        next_page = response.xpath('//a[contains(@class, "i-next")]/@href').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

        links = response.xpath('//li[contains(@class, "product-card")]/a/@href').getall()
        for link in links:
            yield response.follow(link, callback=self.parse_product)

    def parse_product(self, response: HtmlResponse):
        loader = ItemLoader(item=CastoramaparserItem(), response=response)
        loader.add_xpath('_id', '//span[@itemprop="sku"]/text()')
        loader.add_xpath('name', '//h1/text()')
        loader.add_xpath('price', '//div[@class="current-price"]//span[@class="price"]//text()')
        loader.add_xpath('price_old', '//div[@class="old-price"]//span[@class="price"]//text()')
        loader.add_xpath('photos',
                         '//img[@class="zoomImg"]/@src | //div[@class="js-zoom-container"]/img/@data-src')
        loader.add_value('url', response.url)

        yield loader.load_item()
