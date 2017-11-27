import scrapy
import datetime

class ArticleURLSpider(scrapy.Spider):
    name = "article_url_spider"
    custom_settings = {
        "DOWNLOAD_DELAY": 10
    }

    def parse(self, response):
        for article in response.css('div.technologyList section ul li'):
            yield {
                'title': article.css('a::text').extract_first(),
                'url': 'http://apctt.org/' + article.css('a::attr(href)').extract_first().replace('../', '')
            }
