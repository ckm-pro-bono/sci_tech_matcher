import json
import sqlite3
from scrapy.crawler import CrawlerProcess

from src.SectorSpider import SectorSpider

def main():
   # ------- RUN SECTOR CRAWL
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
        'FEED_FORMAT': 'json',
        'FEED_URI': './data/sectors.json'
    })
   
    sector_spider = SectorSpider()
    process.crawl( sector_spider )
   
    process.start()

main()
