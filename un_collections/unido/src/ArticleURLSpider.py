import scrapy
import datetime

class ArticleURLSpider(scrapy.Spider):
    name = "article_url_spider"

    def parse(self, response):
        for article in response.css('li.clfx'):
            yield { "url": article.css('div.text_box h3 a::attr(href)').extract_first() }
