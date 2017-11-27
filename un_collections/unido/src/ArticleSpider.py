import scrapy
import datetime
import pdb
from bs4 import BeautifulSoup
import re
import pandas as pd

class ArticleSpider(scrapy.Spider):
    name = "article_spider"
    custom_settings = {
        "DOWNLOAD_DELAY": 10
    }

    def convert_labels(self, label):
        pass

    def check_for_bad_headers(self, tag):
        return (tag.has_attr('class') and len(tag["class"]) > 1)

    def process_boundary(self, text_tags, boundary):
        first, second = boundary if len(boundary) == 2 else [boundary[0], None]
        label = text_tags[first].text.lower()
        if second:
            raw_content = [tag.text for tag in text_tags[first+1:second] if not self.check_for_bad_headers(tag)]
        else:
            raw_content = [tag.text for tag in text_tags[first+1:] if not self.check_for_bad_headers(tag)]
        content = " ".join(raw_content).replace("\n", " ").replace("\r", " ").strip()
        return (label, content)

    def parse_company_data(self, article):
        company_dict = {}
        company_data_map = {
            'Name': 'company_name',
            'Address': 'company_address',
            'Capital': 'company_capital',
            'Contact person': 'company_contact',
            'Number of employees': 'company_num_employees',
            'Date of company foundation': 'company_founded_date',
            'The type of business': 'company_business_type'
        }
        company_info_elements = article.css('table.cnt-tb1 tr')
        for company_info_row in company_info_elements:
            company_info = company_info_row.css('td::text').extract()
            try:
                company_dict[company_data_map[company_info[0]]] = company_info[1]
            except:
                pass
        return company_dict

    def parse(self, response):
        article = response.css('article#main')

        # extract sections dynamically
        article_soup = BeautifulSoup(article[0].extract(), "lxml")
        text_tags = article_soup.find_all(["p", "h2", "h1", "li", "span", "tr"])
        header_classes = ["title_type_02", "title_type_01", "tech_title"] # "title_type_00"
        boundaries = []
        for index, text_tag in enumerate(text_tags):
            if text_tag.has_attr("class") and len(text_tag["class"]) == 1 and \
                text_tag["class"][0] in header_classes:
                boundaries.append(index)

        first_grouping = [boundaries[index:index+2] for index in range(0, len(boundaries), 2)]
        second_grouping = [boundaries[index+1:index+3] for index in range(0, (len(boundaries)-1), 2)]
        grouped_boundaries = first_grouping + second_grouping
        content = {}
        for boundary in grouped_boundaries:
            result = self.process_boundary(text_tags, boundary)
            content[result[0]] = result[1]

        # remove and replace company data key
        try:
            del content["company data"]
        except:
            pass

        content.update(self.parse_company_data(article))

        # add title and url
        content["title"] = article.css( 'h1.title_type_00::text' ).extract_first()
        content["meta_base_url"] = response.url

            # article_result = {}
            #
            # article_result['applications'] = article.css( '*.title_type_02 ~ p::text' ).extract_first()
            # article_result['title'] = article.css( 'h1.title_type_00::text' ).extract_first()
            # accordion_content = article.css( 'div.accordion_content p' ).extract()
            #
            # for element in accordion_content:
            #     print(element)
            #     try:
            #         if 'advantage' in element.css( '*.title_type_02 *::text').extract_first().lower():
            #             print(element.css( '*.title_type_02::text').exract_first().lower())
            #     except:
            #         pass
            #
            # company_info_elements = article.css('table.cnt-tb1 tr')
            # for company_info_row in company_info_elements:
            #     company_info = company_info_row.css('td::text').extract()
            #
            #     try:
            #         article_result[
            #             company_data_map[ company_info[0] ]
            #         ] = company_info[1]
            #     except:
            #         pass
            #
            # pdb.set_trace()


        yield content
