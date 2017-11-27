import pandas as pd
from selenium import webdriver
from bs4 import BeautifulSoup
import re
import pdb
import urllib.request
from datetime import datetime
import json
from pathos.multiprocessing import ProcessingPool # to allow multiprocessing mapping with class functions
import os

class ScrapeCITTC():

    def __init__(self, driver_path=os.environ['CHROME_DRIVER'], max_val=100):
        self.driver_path = driver_path
        self.browser = webdriver.Chrome(executable_path=driver_path)
        self.headers = {
            "user-agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36(KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36"
        }
        self.max_val = max_val # if you want pages to load faster, reduce max val

        # requests attributes
        self.request_schema = {
            "index": "meta_base_url", "title": "title", "sector": "sector", "Publish": "published",
            "Before": "window", "Country": "country", "Description of Demand": "description",
            "Secondary Field": "secondary_field", "Keywords": "keywords", "Mode of Co-operation": "cooperation_type",
            "Name of Project Owner/ Holders": "contact_organization", "Organization Type": "contact_organization_type",
            "Name": "contact_person", "Employer": "contact_employer", "Email Address": "contact_email",
            "Telephone ": "contact_phone"
        }

        # offers attributes
        self.offer_schema = {
            "index": "meta_base_url", "Publish": "published", "Before": "window", "Country": "country",
            "Region": "region", "Project Description": "description", "Secondary Field": "secondary_field",
            "Technology Readiness Level": "technology_readiness_level", "Keywords": "keywords",
            "Intellectual Property": "intellectual_property_type", "Filing / Grant No": "patent_info",
            "Implementation": "implementation", "Market Prospect": "market_prospect",
            "Mode of Co-operation": "cooperation_type", "Name of Project Owner/Holder": "contact_organization",
            "Organization Type": "contact_organization_type", "Name": "contact_person", "Employer": "contact_employer",
            "E-mail Address": "contact_email", "Telephone": "contact_phone"
        }

    ### retrieve all post links

    def get_total_records(self, url_formatter):
        total_xpath = '//*[@id="list"]/div/span'
        self.browser.get(url_formatter(max_val=1))
        total_element = self.browser.find_element_by_xpath(total_xpath)
        total = int(total_element.get_attribute("innerHTML").replace("&nbsp;", " ").split(" ")[1])
        print("Total records found: %d" % total)
        return total

    def get_query_links(self, url_formatter, total_records):
        query_links = []
        offset_val = 0

        while offset_val < total_records:
            query_links.append(url_formatter(offset_val, self.max_val))
            offset_val += self.max_val

        return query_links

    def calculate_post_range(self, total, offset):
        if total - offset >= self.max_val:
            return range(1, self.max_val + 1)
        return range(1, (total - offset) + 1)

    def get_link_from_post(self, i, offer_post_xpath_formatter):
        post_xpath = offer_post_xpath_formatter(i)
        link_element = self.browser.find_element_by_xpath(post_xpath)
        url = BeautifulSoup(link_element.get_attribute("innerHTML"), "lxml").find("a")["href"]
        return "http://www.cittc.net" + url

    def retrieve_post_links(self, url):
        self.browser.get(url)
        offset = int(re.search('offset=(\d+)', url).groups()[0])
        total_records = self.total_requests if "demand" in url else self.total_offers
        post_range = self.calculate_post_range(total_records, offset)
        return [self.get_link_from_post(i, self.format_request_post_xpath) for i in post_range]

    ### parse data from specific post

    def get_page_html(self, link):
        page_request = urllib.request.Request(link, headers=self.headers)
        page_html = urllib.request.urlopen(page_request).read().decode('utf-8')
        return BeautifulSoup(page_html, "lxml")

    def parse_post_content(self, link):
        detail = self.get_page_html(link)
        row = {}
        row["sector"] = "".join([c for c in detail.find("h3").find("span").text if c.isalpha() or c.isspace()]).strip()
        row["title"] = detail.find("h3")["title"]
        row.update(self.parse_info_div(detail.find("div", id="info")))
        row.update(self.parse_description_div(detail))
        row.update(self.parse_contact_div(detail.find("div", id="contact")))
        return row

    def get_label_content(self, label):
        content = str(label.next_sibling)
        if content != "\n":
            return content
        return label.next_sibling.next_sibling.text.strip()

    def parse_info_div(self, div):
        labels = div.find_all("span")
        content = [self.get_label_content(label) for label in labels]
        return dict(zip([label.text.strip()[:-1] for label in labels], content))

    def parse_description_div(self, detail):
        headers = [label.text[:-1].strip() for label in detail.find("div", id="text").find_all("span")]
        descriptions = [desc.text.strip() for desc in detail.find_all("div", class_="infoin word-break")]
        return dict(zip(headers, descriptions))

    def parse_contact_div(self, div):
        info = div.find_all("output")
        return dict(tuple(pair.text.split(":")) for pair in info)

    ### sanitize post data

    def sanitize_keywords(self, keyword):
        if keyword != "No" and pd.notnull(keyword):
            return keyword.lower().replace(";", ",").replace(",", ", ").replace("  ", " ").replace(" ,", ",")

    def sanitize_title(self, title):
        title = title.strip().replace("  ", " ").replace("“", "")
        return title

    def sanitize_sector(self, sector):
        return sector.replace("   ", " ")

    def add_meta_fields(self, data, category):
        data["meta_organization"] = "CITTC"
        data["meta_category"] = category
        data["meta_collected_date"] = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
        return data

    ### write
    def write_json(self, data, file_name):
        print("Writing JSON to {}".format(file_name))
        with open(file_name, "w") as f:
            json_data = data.to_json(orient="records")
            f.write(json_data)

    def write_csv(self, data, file_name):
        print("Writing CSV to {}".format(file_name))
        data.to_csv(file_name, index=False, encoding="utf-8")


    ### REQUESTS

    def format_requests_url(self, offset_val=0, max_val=100):
        return "http://www.cittc.net/english/demandList.html?offset={}&max={}".format(offset_val, max_val)

    def format_request_post_xpath(self, i):
        return '//*[@id="list"]/ul/li[{}]/div[6]'.format(i)

    def retrieve_requests(self):
        print("REQUESTS")
        print("\nRetrieve Total Requests\n------------------------------")
        self.total_requests = self.get_total_records(self.format_requests_url)

        print("\nRetrieve Request Links\n------------------------------")
        query_links = self.get_query_links(self.format_requests_url, self.total_requests)
#         request_links = ProcessingPool().amap(self.retrieve_post_links, query_links) # int error??
        request_links = []
        for link in query_links:
            print("Processing %s" % link)
            request_links = request_links + self.retrieve_post_links(link)

        print("\nRetrieve Content\n------------------------------")
        raw_request_content = ProcessingPool().map(self.parse_post_content, request_links)
        self.raw_requests = pd.DataFrame(raw_request_content)
        self.raw_requests["meta_base_url"] = request_links
        print("{} requests parsed for content".format(len(self.raw_requests)))

        print("\nSanitize Content\n------------------------------")
        self.requests = self.raw_requests.copy()

        print("Applying schema")
        self.requests.rename(columns=self.request_schema, inplace=True)
        self.requests = self.requests[list(self.request_schema.values())]

        print("Sanitizing values")
        self.requests["title"] = self.requests["title"].apply(self.sanitize_title)
        self.requests["keywords"] = self.requests["keywords"].apply(self.sanitize_keywords)
        self.requests["sector"] = self.requests["sector"].apply(self.sanitize_sector)
        self.requests = self.add_meta_fields(self.requests, "request")

        print("{} requests processed".format(len(self.requests)))

    ### OFFERS

    def format_offers_url(self, offset_val=0, max_val=100):
        return "http://www.cittc.net/english/supplyList.html?offset={}&max={}".format(offset_val, max_val)

    def format_offer_post_xpath(self, i):
        return '//*[@id="list"]/ul/li[{}]/div[1]'.format(i)

    def retrieve_offers(self):
        print("OFFERS")
        print("\nRetrieve Total Offers\n------------------------------")
        self.total_offers = self.get_total_records(self.format_offers_url)

        print("\nRetrieve Offer Links\n------------------------------")
        query_links = self.get_query_links(self.format_offers_url, self.total_offers)
#         request_links = ProcessingPool().amap(self.retrieve_post_links, query_links) # int error??
        offer_links = []
        for link in query_links:
            print("Processing %s" % link)
            offer_links = offer_links + self.retrieve_post_links(link)

        print("\nRetrieve Content\n------------------------------")
        raw_offer_content = ProcessingPool().map(self.parse_post_content, offer_links)
        self.raw_offers = pd.DataFrame(raw_offer_content)
        self.raw_offers["meta_base_url"] = request_links
        print("{} offers parsed for content".format(len(self.raw_offers)))

        print("\nSanitize Content\n------------------------------")
        self.offers = self.raw_offers.copy()

        print("Applying schema")
        self.offers.rename(columns=self.offer_schema, inplace=True)
        self.offers[list(self.offer_schema.values())]

        print("Sanitizing values")
        self.offers["title"] = self.offers["title"].apply(self.sanitize_title)
        self.offers["keywords"] = self.offers["keywords"].apply(self.sanitize_keywords)
        self.offers["sector"] = self.offers["sector"].apply(self.sanitize_sector)
        self.offers = self.add_meta_fields(self.offers, "offer")

        print("{} offers processed".format(len(self.offers)))
