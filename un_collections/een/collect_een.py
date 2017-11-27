import re
import os
import time
import sqlite3
import pickle
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException
from bs4 import BeautifulSoup
from collections import namedtuple


SearchResult = namedtuple('SearchResult', ['title',
                                           'link',
                                           'country',
                                           'type',
                                           'publish_date'])

PartneringOp = namedtuple('PartneringOp',
                          ['meta_organization',
                           'meta_category',
                           'meta_collected_date',
                           'meta_base_url',
                           'title',
                           'publish_date',
                           'country',
                           'type',
                           'pod_reference',
                           'summary',
                           'description',
                           'advantages',
                           'stage_of_development',
                           'development_comments',
                           'ipr_status',
                           'profile_origin',
                           'technology_keywords',
                           'market_keywords',
                           'nace_keywords',
                           'partner_sought_role',
                           'partner_sought_size',
                           'partnership_type_considered',
                           'client_type',
                           'client_year_est',
                           'client_transnational_coop',
                           'client_comments',
                           'client_languages',
                           'client_country',
                           'sector_group'])

# Get the total number of results returned by empty search
def get_num_results(search_result_soup):
    num = search_result_soup.find("div", id="resultCount").strong.text.strip()
    return int(num)

# Mutate driver arg to move to next result page
def next_result(driver):
    driver.find_element_by_link_text("Next").click()

# Move forward in search results by calling next_callable on driver
def seek(driver, num_collected, next_callable, results_per_page):
    for i in range(0, num_collected // results_per_page):
        next_callable(driver)
        time.sleep(3)

def _seek(driver, next_callable, count):
    for i in range(0, count):
        next_callable(driver)
        time.sleep(3)

def get_current_page(soup):
    cur = soup.find("a", class_="t-state-active mpager").text
    return int(cur) if cur else None

# Transform search results page
def parse_results(search_page):
    results = []
    for x in search_page.findAll("tr", class_=re.compile("SHrow(.*)")):
        results.append(SearchResult(x.find("a").text.strip(),
                              x.find("a")["href"],
                              x.find("td", class_="SHcountry").text.strip(),
                              x.find("td", class_="SHoffer").text.strip(),
                              x.find("td", class_="SHdate").text.strip()))
    return results

# Parse partnering opportunity page, return dict with native keys
def parse_single_result(soup):
    data = {}
    for fs in soup.findAll("fieldset"):
        for tr in fs.findAll("tr"):
            name = tr.find("td").text.strip()
            val = tr.find("td").next_sibling.next_sibling.text.strip()
            data[name] = val
    return data

# Construct a row for database based on schema
def partner_op(search_result, res):
    return PartneringOp(meta_organization = 'een',
                        meta_category = 'offer',
                        meta_collected_date = '11-11-2017',
                        meta_base_url = BASE,
                        title = res.get('Title', ''),
                        publish_date = search_result.publish_date,
                        country = search_result.country,
                        type = search_result.type,
                        pod_reference = res.get('POD Reference', ''),
                        summary = res.get('Summary', ''),
                        description = res.get('Description', ''),
                        advantages = res.get('Advantages and Innovations', ''),
                        stage_of_development = res.get('Stage of Development', ''),
                        development_comments = '',
                        ipr_status = res.get('IPR Status', ''),
                        profile_origin = res.get('Profile Origin', ''),
                        technology_keywords = res.get('Technology Keywords', ''),
                        market_keywords = res.get('Market Keywords', ''),
                        nace_keywords = res.get('NACE Keywords', ''),
                        partner_sought_role = res.get('Type and Role of Parter Sought', ''),
                        partner_sought_size = res.get('Type and Size of Partner Sought', ''),
                        partnership_type_considered = res.get('Type of Partnership Considered', ''),
                        client_type = res.get('Type and Size of Client', ''),
                        client_year_est = res.get('Year Established', ''),
                        client_transnational_coop = res.get('Already Engaged in Trans-National Cooperation',''),
                        client_comments = '',
                        client_languages = res.get('Languages Spoken', ''),
                        client_country = res.get('Client Country', ''),
                        sector_group = res.get('Sector Group', ''))

DRIVER_PATH = os.environ['CHROME_DRIVER']
HEADLESS = True
START = 'http://een.ec.europa.eu/tools/services/SearchCenter/Search/ProfileSimpleSearch'
DB_PATH = 'een.db'
BASE = 'http://een.ec.europa.eu'

if HEADLESS:
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('window-size=1200x600')
    driver = webdriver.Chrome(executable_path=DRIVER_PATH,
                              chrome_options=options)
else:
    driver = webdriver.Chrome(executable_path=DRIVER_PATH)

con = sqlite3.connect(DB_PATH)

if os.path.isfile('last_page.pickle'):
    with open('last_page.pickle', 'rb') as f:
      last_page = pickle.load(f)
else:
    last_page = 0
    with open('last_page.pickle', 'wb') as f:
        pickle.dump(last_page, f)

driver.get(START)
driver.find_element_by_id("advancedsearchbutton").click()
time.sleep(2)

MAIN_TAB = driver.window_handles[0]
tabs = ["tab{}".format(i) for i in range(0, 25)]

for tab in tabs:
    driver.execute_script("window.open('about:blank', '{}');".format(tab))

soup = BeautifulSoup(driver.page_source, 'html.parser')
current_page = get_current_page(soup)
num_results = get_num_results(soup)
num_collected = con.execute("select count(*) from partnering_opportunity").fetchone()[0]

print("current page: {}".format(current_page))
print("last page on disk: {}".format(last_page))
print("total results to collect: {}".format(num_results))
print("num collected: {}".format(num_collected))


while last_page < num_results // 25:

    # Seek forward in result to target page
    while current_page < last_page + 1:
        print("current page: {}".format(current_page))
        print("seeking to target page: {}".format(last_page + 1))
        while True:
            try:
                nxt = WebDriverWait(driver, 50).until(EC.element_to_be_clickable((By.LINK_TEXT, "Next")))
                time.sleep(2)
                nxt.click()
                time.sleep(2)
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                current_page = get_current_page(soup)
                break
            except WebDriverException:
                pass

    print("Seeking stopped. Collecting results of current page {}".format(current_page))

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    results = parse_results(soup)
    batch = []
    
    for tab, result in zip(tabs, results):
        driver.switch_to_window(tab)
        driver.get(BASE + result.link)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        data = parse_single_result(soup)
        batch.append(partner_op(result, data))
        time.sleep(.5)

    df = pd.DataFrame.from_records(batch, columns=PartneringOp._fields)

    try:
        df.to_sql('partnering_opportunity', con, if_exists='append', index=False)
        print("Collected page '{}'\n".format(current_page))
    except sqlite3.IntegrityError as e:
        print(e)
        pass

    driver.switch_to_window(MAIN_TAB)
    time.sleep(3)

    num_collected = con.execute("select count(*) from partnering_opportunity").fetchone()[0]
    print("Collected {} of {} partnering opportunities\n".format(num_collected, num_results))

    print("Setting last page to {}".format(last_page + 1))

    last_page += 1
    with open('last_page.pickle', 'wb') as f:
        pickle.dump(last_page, f)
    

