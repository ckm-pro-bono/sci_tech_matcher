import json
import sqlite3
from scrapy.crawler import CrawlerProcess

from src.SectorSpider import SectorSpider
from src.ArticleURLSpider import ArticleURLSpider
from src.ArticleSpider import ArticleSpider

def main():
    # ------- RUN SECTOR CRAWL
#    process = CrawlerProcess({
#        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
#        'FEED_FORMAT': 'json',
#        'FEED_URI': './data/sectors.json'
#    })

#    sector_spider = SectorSpider()
#    process.crawl( sector_spider )

#    process.start()

    # ------- RUN ARTICLE URL CRAWLS
#    with open('./data/sectors.json', 'r') as sector_file:
#        sectors_data = sector_file.read()

#    sector_article_urls = []
#    for sector_data in json.loads(sectors_data):
#        sector_article_urls.append( sector_data['url'] )

#    process = CrawlerProcess({
#        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
#        'FEED_FORMAT': 'json',
#        'FEED_URI': './data/article_urls.json'
#    })

#    process.crawl( ArticleURLSpider, start_urls = sector_article_urls  )
#    process.start()

    # -------- RUN ARTICLE CRAWLS
    with open('./data/article_urls.json', 'r') as article_url_file:
        article_url_data = article_url_file.read()

    article_urls = []
    for article_url_data in json.loads(article_url_data):
        article_urls.append( article_url_data['url'] )

    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
        'FEED_FORMAT': 'json',
        'FEED_URI': './data/articles.json'
    })

    process.crawl( ArticleSpider, start_urls = article_urls  )
    process.start()


main()
