import numpy as np
import pandas as pd
import numpy as np
import os
import requests
import pdb
import datetime
from bs4 import BeautifulSoup
from selenium import webdriver 
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as wait

from io import BytesIO
from pdfminer.pdfparser import PDFParser, PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox, LTTextLine, LTTextBoxHorizontal
# from pdfminer.pdfpage import PDFTextExtractionNotAllowed


CHROME_PATH = os.environ['CHROME_DRIVER']
DRIVER = webdriver.Chrome(CHROME_PATH)
BASE_LINK = "http://unfccc.int/ttclear/projects"
SEEKING_SUPPORT_XPATH = """//*[@id="inner4-section1"]/div/div/div/div/div[2]/div[1]/div[1]/a"""
SUPPORTED_XPATH = """//*[@id="inner4-section1"]/div/div/div/div/div[2]/div[1]/div[2]/a"""

def get_html():
    browser = DRIVER.find_element_by_id("accordion3")
    button = wait(browser, 10).until(EC.presence_of_element_located((By.CLASS_NAME,"accordion-group")))
    button.click()
    html = DRIVER.page_source
    soup = BeautifulSoup(html,"lxml")
    return soup
    
def parse_raw_elements(soup):
    accordion_elements = [el.text for el in soup.find_all('div', class_='inner-pad')][3:]      

    posts = pd.DataFrame([dict(zip(["sector", "keywords", "region"], accordion_elements[n:n+3])) for n in range(0, len(accordion_elements), 3)])

    pdf_links = [el.find('a')['href'] for el in soup.find_all('div', class_='col-md-3 text-center-xs')]
    pdf_links = pd.Series(pdf_links[1:]).str.replace(" ", "%20")
    posts["document_url"] = pdf_links

    titles = [el.text for el in soup.findAll('div', class_='content-box-data')]
    titles = pd.Series(titles[1:])
    posts["title"] = titles
    return posts

def parse_title(title):
    title = title.replace('\n\n','\n')
    breakdown = title.split("\n")
    breakdown = dict(zip(["title", "date_posted", "country", "project_type"], title.split("\n")[1:-1]))
    return pd.Series(breakdown)

def get_summary_from_pdf(link):
    print("Parsing %s" % link)
    try:
        raw_content = BytesIO(requests.get(link, timeout=(5, 30)).content) # turn content into a file-like object that allows seek
        parser = PDFParser(raw_content)
        document = PDFDocument()
        parser.set_document(document)
        document.set_parser(parser)
        document.initialize('')
        rsrcmgr = PDFResourceManager()
        laparams = LAParams()
        device = PDFPageAggregator(rsrcmgr, laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        extracted_text = ''

        for page in document.get_pages():
            interpreter.process_page(page)
            layout = device.get_result()
            for element in layout:
                if isinstance(element, LTTextBoxHorizontal):
                    extracted_text += element.get_text()

        content = [line.strip().replace("\n", " ") for line in extracted_text.split(" ") if line != "\n"]
        return " ".join(content[:500])
    except:
        return "Unable to parse"


def clean_elements(raw_data, seeking_support):
    clean_data = raw_data.copy()
    clean_data["region"] = clean_data["region"].str.replace('\nRegion\n','').str.strip()
    clean_data["keywords"] = clean_data["keywords"].str.replace('\nKeywords\n','').str.strip().str.lower()
    clean_data["sector"] = clean_data["sector"].str.replace('\nSectors\n','').str.strip()

    title_breakdown = clean_data["title"].apply(parse_title)
    del clean_data["title"]
    clean_data = pd.concat([clean_data,title_breakdown], axis=1)
    
    clean_data["summary"] = clean_data["document_url"].apply(get_summary_from_pdf)

    clean_data['seeking_support'] = seeking_support 
    return clean_data
    
def run_scraper(seeking_support=True):
    soup = get_html()
    raw_data = parse_raw_elements(soup)
    clean_data = clean_elements(raw_data, seeking_support)
    message = "projects seeking support" if seeking_support else "supported projects"
    print("Found %d %s" % (len(clean_data), message))
    return clean_data
    
##### open page and extract HTML

print("Launching request to %s" % BASE_LINK)
DRIVER.get("http://unfccc.int/ttclear/projects")
    
##### parse projects seeking support

print("\nParsing projects seeking support")
DRIVER.find_element_by_xpath(SEEKING_SUPPORT_XPATH).click()
projects_seeking_support = run_scraper()

##### parse supported projects

print("\nParsing supported projects")
DRIVER.find_element_by_xpath(SUPPORTED_XPATH).click()
supported_projects = run_scraper(seeking_support=False)

##### join both datasets and add metadata

unfccc_data = pd.concat([projects_seeking_support,supported_projects])
unfccc_data.reset_index(drop=True)

unfccc_data['meta_organization'] = 'unfccc'
unfccc_data['meta_category'] = "climate_tech_project"
unfccc_data['meta_collected_date'] = datetime.datetime.utcnow()
unfccc_data['meta_base_url'] = 'http://unfccc.int/ttclear/'

print("\nResult:")
print("%d total projects" % len(unfccc_data))
print(unfccc_data.sample(3))

print("\Writing CSV")
unfccc_data.to_csv("unfccc_data_with_summaries.csv", index=False)

