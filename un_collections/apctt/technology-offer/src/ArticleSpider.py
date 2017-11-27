import scrapy
import datetime

class ArticleSpider(scrapy.Spider):
    name = "article_spider"
    custom_settings = {
        "DOWNLOAD_DELAY": 10
    }

    def parse(self, response):
        article = response.css('div.view-content')[0]
        description = article.css('div.webform-long-answer::text').extract_first()

        try:
            if len(description) > 150:
                description = description[0:150]
        except:
            description = ''

        yield {
            'title': article.css('div.views-row:nth-child(1) div:nth-child(1) h3:nth-child(1)::text').extract_first(),
            'description': description,
            'url': response.url, 
            'sector': article.css('div.views-row:nth-child(1) div:nth-child(3) span.field-content::text').extract_first(),
            'country': article.css('div.views-row:nth-child(1) div:nth-child(4) span.field-content::text').extract_first(),
            'area of application': article.css('div.views-row:nth-child(1) div:nth-child(5) span.field-content::text').extract_first(),
            'keywords': article.css('div.views-row:nth-child(1) div:nth-child(6) span.field-content::text').extract_first(),
            'advantages': article.css('div.views-row:nth-child(1) div:nth-child(7) span.field-content::text').extract_first(),
            'environmental_aspects': article.css('div.views-row:nth-child(1) div:nth-child(8) span.field-content::text').extract_first(),
            'development_status': article.css('div.views-row:nth-child(1) div:nth-child(9) span.field-content::text').extract_first(),
            'legal_protection': article.css('div.views-row:nth-child(1) div:nth-child(10) span.field-content::text').extract_first(),
            'tech_specifications': article.css('div.views-row:nth-child(1) div:nth-child(11) span.field-content::text').extract_first(),
            'transfer_terms': article.css('div.views-row:nth-child(1) div:nth-child(12) span.field-content::text').extract_first(),
            'target_countries': article.css('div.views-row:nth-child(1) div:nth-child(13) span.field-content::text').extract_first(),
            'estimated_cost': article.css('div.views-row:nth-child(1) div:nth-child(14) span.field-content::text').extract_first(),
            'contact_person': article.css('div.views-row:nth-child(1) div:nth-child(16) span.field-content::text').extract_first(),
            'contact_address': article.css('div.views-row:nth-child(1) div:nth-child(17) span.field-content::text').extract_first(),
            'contact_city': article.css('div.views-row:nth-child(1) div:nth-child(18) span.field-content::text').extract_first(),
            'contact_zip': article.css('div.views-row:nth-child(1) div:nth-child(19) span.field-content::text').extract_first()
        }
