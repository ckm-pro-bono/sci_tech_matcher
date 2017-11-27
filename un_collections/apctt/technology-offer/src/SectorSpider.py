import scrapy
import datetime

class SectorSpider(scrapy.Spider):
    name = "sector_spider"
    start_urls = [
        'http://apctt.org/technology-offer/'
    ]

    custom_settings = {
        "DOWNLOAD_DELAY": 5,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 2
    }

    def parse(self, response):
        for sector in response.css('div.technologyList section ul li'):
            yield {
                'sector': sector.css('a::text').extract_first(),
                'url': "http://apctt.org/" + sector.css('a::attr(href)').extract_first()
            }
