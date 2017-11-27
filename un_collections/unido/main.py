import json
import sqlite3
from scrapy.crawler import CrawlerProcess
from src.ArticleSpider import ArticleSpider
from src.ArticleURLSpider import ArticleURLSpider
import ast
import pdb
import pandas as pd

import sanitize

def get_urls():
    """writes all UNIDO urls to scrape to `articles_urls.txt`"""
    start_urls = [
           'http://www.unido.or.jp/en/activities/technology_transfer/technology_db/low_carbon/',
           'http://www.unido.or.jp/en/activities/technology_transfer/technology_db/pollution/',
           'http://www.unido.or.jp/en/activities/technology_transfer/technology_db/waste_treatment/'
    ]
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
        'FEED_FORMAT': 'json',
        'FEED_URI': './data/article_urls.txt'
    })

    process.crawl( ArticleURLSpider, start_urls = start_urls )
    process.start()

def scrape():
    # ------- RUN ARTICLE CRAWLS
    with open('./data/article_urls.txt', 'r') as article_url_file:
        article_url_data = article_url_file.read()

    article_urls = []
    for article_url in article_url_data[1:-2].split(','):
        article_urls.append( json.loads(article_url)['url'] )

    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
        'FEED_FORMAT': 'json',
        'FEED_URI': './data/raw_article_content.json'
    })

    process.crawl( ArticleSpider, start_urls = article_urls )
    process.start()

# scrape()
sanitized_data = sanitize.run()

def save_to_db():
        # ------- SAVE TO SQLITE
       articles = json.load( open('./data/articles.json') )
       connection = sqlite3.connect('./data/unido.db')
       curr = connection.cursor()

       try:
           curr.execute('''CREATE TABLE articles
                    (meta_organization TEXT NOT NULL,
                   meta_category TEXT NOT NULL,
                   meta_collected_date TEXT NOT NULL,
                   meta_base_url TEXT NOT NULL,
                   title TEXT NOT NULL,
                   description TEXT,
                   sector TEXT,
                   registered_category TEXT,
                   features_and_advantages TEXT,
                   applications TEXT,
                   competitive_advantage TEXT,
                   performance TEXT,
                   technical_maturity TEXT,
                   risk TEXT,
                   patent_info TEXT,
                   company_name TEXT,
                   company_address TEXT,
                   company_capital TEXT,
                   company_contact TEXT,
                   company_num_employees TEXT,
                   company_founded_date TEXT,
                   company_business_type TEXT,
                   modality_of_transaction TEXT)'''
           )
       except:
           pass

       query = """
           INSERT INTO articles
           VALUES (?,?,?,?,?,?,?,?)
       """

       columns = [
           'applications',               # ok
           'company_address',            # ok
           'competitive_advantage',      #
           'company_business_type',      # ok
           'company_capital',            # ok
           'company_contact',            # ok
           'company_founded_date',       # ok
           'company_name',               # ok
           'company_num_employees',      # ok
           'description',
           'features_and_advantages',    #
           'meta_base_url',
           'meta_category',
           'meta_collected_date',
           'meta_organization',
           'modality_of_transaction',    #
           'patent_info',                #
           'performance',                #
           'registered_category',        #
           'risk',                       #
           'sector',
           'technical_maturity',         #
           'title' #ok
       ]

       for data in articles:
           data = tuple( data[column] for column in columns )
           curr.execute( query, data )

       connection.commit()
       connection.close()
