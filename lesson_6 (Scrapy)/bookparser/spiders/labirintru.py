import scrapy
from scrapy.http import HtmlResponse

from bookparser.items import BookparserItem


class LabirintruSpider(scrapy.Spider):
    name = 'labirintru'
    allowed_domains = ['labirint.ru']
    query = 'python'
    start_urls = [f'https://www.labirint.ru/search/{query}/?stype=0']

    def parse(self, response: HtmlResponse):
        nex_page = response.xpath("//div[@class='pagination-next']/a/@href").get()
        if nex_page:
            yield response.follow(nex_page, callback=self.parse)

        links = response.xpath("//a[@class='cover']/@href").getall()
        for link in links:
            yield response.follow(link, callback=self.book_parse)

    def book_parse(self, response: HtmlResponse):
        full_title = response.xpath("//h1/text()").get().split(': ')
        
        _id = response.xpath("//div[@class='isbn']/text()").get().split(' ')[1].replace('\xa0', '')
        author = full_title[0]
        title = ': '.join(full_title[1:])
        price_old = response.xpath("//span[contains(@class, 'priceold')]/text()").get()
        price_new = response.xpath("//span[contains(@class, 'pricenew')]/text()").get()
        rating = float(response.xpath("//div[@id='rate']/text()").get())
        url = response.url

        try:
            price_old = int(price_old)
            price_new = int(price_new)
        except Exception:
            pass

        yield BookparserItem(
            _id=_id,
            author=author,
            title=title,
            price_old=price_old,
            price_new=price_new,
            rating=rating,
            url=url
        )
