
# coding: utf-8

# # UN Scraping of UNFCC website: http://unfccc.int/ttclear/

# http://unfccc.int/ttclear/projects
import numpy as np
import pandas as pd
import numpy as np
import os
import requests
from bs4 import BeautifulSoup
from selenium import webdriver 
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as wait


chrome_path = os.environ['CHROME_DRIVER']
driver = webdriver.Chrome(chrome_path)
driver.get("http://unfccc.int/ttclear/projects")

#clicks the project seeking support tab
driver.find_element_by_xpath("""//*[@id="inner4-section1"]/div/div/div/div/div[2]/div[1]/div[1]/a""").click()
#driver.find_element_by_xpath("""//*[@id="inner4-section1"]/div/div/div/div/div[2]/div[1]/div[2]/a""").click()

    
browser = driver.find_element_by_id("accordion3")
button = wait(browser, 10).until(EC.presence_of_element_located((By.CLASS_NAME,"accordion-group")))
button.click()

html = driver.page_source
soup = BeautifulSoup(html,"lxml")


# # Project Seeking Support tab

# In[3]:


accordion_elements = [el.text for el in soup.find_all('div', class_='inner-pad')]
accordion_elements = accordion_elements[3:]
print(len(accordion_elements)) #length 1881 and then 627 for each
print(accordion_elements[0:10])


# In[4]:


#sectors
sectors = accordion_elements[::3]
sectors = np.asarray(sectors)
print(len(sectors))
print((sectors[0:10]))


# In[5]:


#keywords
accordion_elements = accordion_elements[1:]
keywords = accordion_elements[::3]
keywords = np.asarray(keywords)
print(len(keywords))
print((keywords[0:10]))


# In[6]:


#regions
accordion_elements = accordion_elements[1:]
regions = accordion_elements[::3]
regions = np.asarray(regions)
print(len(regions))
print((regions[0:10]))


# In[7]:


#GET PDF LINKS
pdfs = [el.find('a')['href'] for el in soup.find_all('div', class_='col-md-3 text-center-xs')]
pdfs = pdfs[1:]
pdfs = np.asarray(pdfs)
print(len(pdfs))
print(pdfs[0:10])



# In[8]:


#TITLES
titles = [el.text for el in soup.findAll('div', class_='content-box-data')]
titles = titles[1:]
titles = np.asarray(titles)
print(len(titles))
print(titles[0:10])


# In[9]:


projects_seeking_support = pd.DataFrame({'title': titles, 'region': regions, 'sector': sectors, 'document_url': pdfs, 'keywords': keywords})



# # Supported Projects tab

# In[10]:


chrome_path = os.environ['CHROME_DRIVER']


driver = webdriver.Chrome(chrome_path)
driver.get("http://unfccc.int/ttclear/projects")

#clicks the supported projects tab
driver.find_element_by_xpath("""//*[@id="inner4-section1"]/div/div/div/div/div[2]/div[1]/div[2]/a""").click()

    
browser = driver.find_element_by_id("accordion3")
button = wait(browser, 10).until(EC.presence_of_element_located((By.CLASS_NAME,"accordion-group")))
button.click()

html = driver.page_source
soup = BeautifulSoup(html,"lxml")


# In[11]:


accordion_elements = [el.text for el in soup.find_all('div', class_='inner-pad')]
accordion_elements = accordion_elements[3:]
print(len(accordion_elements)) #length 1881 and then 627 for each
print(accordion_elements[0:10])


# In[12]:


#sectors
sectors = accordion_elements[::3]
sectors = np.asarray(sectors)
print(len(sectors))
print((sectors[0:10]))


# In[13]:


#keywords
accordion_elements = accordion_elements[1:]
keywords = accordion_elements[::3]
keywords = np.asarray(keywords)
print(len(keywords))
print((keywords[0:10]))


# In[14]:


#regions
accordion_elements = accordion_elements[1:]
regions = accordion_elements[::3]
regions = np.asarray(regions)
print(len(regions))
print((regions[0:10]))


# In[15]:


#GET PDF LINKS
pdfs = [el.find('a')['href'] for el in soup.find_all('div', class_='col-md-3 text-center-xs')]
pdfs = pdfs[1:]
pdfs = np.asarray(pdfs)
print(len(pdfs))
print(pdfs)



# In[16]:


#TITLES
titles = [el.text for el in soup.findAll('div', class_='content-box-data')]
titles = titles[1:]
titles = np.asarray(titles)
print(len(titles))
print(titles[0:10])


# In[17]:


supported_projects = pd.DataFrame({'title': titles, 'region': regions, 'sector': sectors, 'document_url': pdfs, 'keywords': keywords})


# #  CLEANING SEEKING SUPPORT DATAFRAME

# In[18]:


projects_seeking_support['region'] = projects_seeking_support['region'].str.replace('\nRegion\n','')
projects_seeking_support['region'] = projects_seeking_support['region'].str.replace('\n','')

projects_seeking_support['sector'] = projects_seeking_support['sector'].str.replace('\nSectors\n','')
projects_seeking_support['sector'] = projects_seeking_support['sector'].str.replace('\n','')


projects_seeking_support['keywords'] = projects_seeking_support['keywords'].str.replace('\nKeywords\n','')
projects_seeking_support['keywords'] = projects_seeking_support['keywords'].str.replace('\n','')


projects_seeking_support['title'] = projects_seeking_support['title'].str.replace('\n\n','\n')

#PARSE TITLE
x = projects_seeking_support['title'].apply(lambda x: pd.Series(x.split('\n')))
x = x.rename(columns={1: 'title', 2: 'date_posted', 3: 'country', 4: 'project_type'})
x.drop([5], axis = 1, inplace = True)
x.drop([0], axis = 1, inplace = True)

projects_seeking_support = projects_seeking_support.rename(columns={'title': 'old_title'})




# In[19]:


projects_seeking_support = projects_seeking_support.join(x)
projects_seeking_support.drop(['old_title'], axis = 1, inplace = True)


# In[20]:


projects_seeking_support['seeking_support'] = True 


# #  CLEANING SUPPORTED PROJECTS DATAFRAME

# In[21]:


supported_projects['region'] = supported_projects['region'].str.replace('\nRegion\n','')
supported_projects['region'] = supported_projects['region'].str.replace('\n','')

supported_projects['sector'] = supported_projects['sector'].str.replace('\nSectors\n','')
supported_projects['sector'] = supported_projects['sector'].str.replace('\n','')


supported_projects['keywords'] = supported_projects['keywords'].str.replace('\nKeywords\n','')
supported_projects['keywords'] = supported_projects['keywords'].str.replace('\n','')


supported_projects['title'] = supported_projects['title'].str.replace('\n\n','\n')

#PARSE TITLE
x = supported_projects['title'].apply(lambda x: pd.Series(x.split('\n')))
x = x.rename(columns={1: 'title', 2: 'date_posted', 3: 'country', 4: 'project_type'})
x.drop([5], axis = 1, inplace = True)
x.drop([0], axis = 1, inplace = True)

supported_projects = supported_projects.rename(columns={'title': 'old_title'})


# In[22]:


supported_projects = supported_projects.join(x)
supported_projects.drop(['old_title'], axis = 1, inplace = True)
supported_projects['seeking_support'] = False 


# # AGGREGATE  projects_seeking_support and supported_projects and add meta data

# In[23]:


print(projects_seeking_support.columns.values)
print('hiro')
print(supported_projects.columns.values)


# In[24]:


unfccc_data = pd.concat([projects_seeking_support,supported_projects])


# In[25]:


import datetime

unfccc_data['meta_organization'] = 'unfccc'
unfccc_data['meta_category'] = "climate_tech_project"
unfccc_data['meta_collected_date'] = datetime.datetime.utcnow()
unfccc_data['meta_base_url'] = 'http://unfccc.int/ttclear/'


# In[26]:


unfccc_data = unfccc_data.reset_index(drop=True)
print(unfccc_data.shape)
unfccc_data


# # Put Data into sqllite db

# In[27]:


import sqlite3
conn = sqlite3.connect('unfccc.db')


# In[28]:


unfccc_data.to_sql(name='unfccc', con=conn)


# In[ ]:


#Converts notebook to script
get_ipython().system('jupyter nbconvert --to script Web_Scraping.ipynb')
#unfccc_data.to_csv('unfccc_data.csv', sep=',', encoding='utf-8')

