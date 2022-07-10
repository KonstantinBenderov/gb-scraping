import requests
from lxml import html
from pymongo import MongoClient

# Settings
client = MongoClient('127.0.0.1', 27017)
db = client['gb-scraping']
db_news = db.news

url = 'https://news.mail.ru/'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 '
                         '(KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'}
session = requests.Session()
response = session.get(url, headers=headers)
dom = html.fromstring(response.text)

# Main block of news
news_block = dom.xpath('.//div[@data-logger="news__MainTopNews"]//@href')

# Get links to news
links = []
[links.append(link) for link in news_block if link not in links]

new_news = 0
old_news = 0
for link in links:
    _news = {}
    _response = session.get(link, headers=headers)
    _dom = html.fromstring(_response.text)
    _news_block = _dom.xpath('.//div[@data-news-id]')[0]

    _id = [x for x in link.split('/') if x][-1]
    _news['_id'] = _id
    _news['link'] = link
    _news['title'] = _news_block.xpath('.//h1/text()')[0]
    _news['description'] = _news_block.xpath('.//p/text()')[0].replace('\xa0', ' ')
    _news['date'] = _news_block.xpath('.//span/@datetime')[0]
    _news['source'] = _news_block.xpath('.//@href')[0]

    # Check db for a record
    has_news = bool(db_news.find_one({'_id': _id}))
    if has_news:
        # If yes - overwrite (may be updated)
        db_news.replace_one({'_id': _id}, _news)
        old_news += 1
    else:
        # If not - insert news in db
        db_news.insert_one(_news)
        new_news += 1
else:
    # Final message
    print(f'Total in db: {len(list(db_news.find({}))):5} news')
    print(f'  New added: {new_news:5} news')
    print(f'    Updated: {old_news:5} news')
