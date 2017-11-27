import json
import sqlite3
from scrapy.crawler import CrawlerProcess

from src.ArticleURLSpider import ArticleURLSpider

def main():

    # ------- RUN ARTICLE URL CRAWLS
    with open('./data/sectors.json', 'r') as sector_file:
        sectors_data = sector_file.read()
   
    sector_article_urls = []
    for sector_data in json.loads(sectors_data):
        sector_article_urls.append( sector_data['url'] )
   
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
        'FEED_FORMAT': 'json',
        'FEED_URI': './data/article_urls.json'
    })
   
    process.crawl( ArticleURLSpider, start_urls = sector_article_urls  )
    process.start()


main()
