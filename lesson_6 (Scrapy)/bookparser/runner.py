from scrapy.crawler import CrawlerRunner
from twisted.internet import reactor
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings

from bookparser.spiders.labirintru import LabirintruSpider

if __name__ == '__main__':
    configure_logging()
    settings = get_project_settings()
    runner = CrawlerRunner(settings)
    runner.crawl(LabirintruSpider)

    d = runner.join()
    d.addBoth(lambda _: reactor.stop())
    reactor.run()
