import json
import pandas as pd
from datetime import datetime
import pdb

LABEL_MAP = {
    "competitive advantage": "competitive_advantage",
    'competitive advantages': "competitive_advantage",
    "performance": "performance",
    "pferformance": "performance",
    "conceivable risk": "risk",
    "conceivable applications": "applications",
    "registered category": "registered_category",
    'modality of business transaction': "modality_of_transaction",
    'information of patent related to this technology': "patent_info",
    'information on patent related to this technology': "patent_info",
    'information on patent related to this technology (if applicable)': "patent_info",
    'major features and advantages': "features_and_advantages",
    '\nmajor features and advantages': "features_and_advantages",
    'technical maturity': "technical_maturity",
    'technical maturity / past record of introduction': "technical_maturity",
    'technology data': "technical_maturity",
    "company_name": "company_name",
    'company_address': "company_address",
    'company_business_type': 'company_business_type',
    'company_capital': 'company_capital',
    'company_contact': 'company_contact',
    'company_founded_date': 'company_founded_date',
    'company_num_employees': 'company_num_employees',
    "title": "title",
    "description": "description",
    "meta_base_url": "meta_base_url",
    "meta_organization": "meta_organization",
    "meta_category": "meta_category",
    "meta_collected_date": "meta_collected_date"
}

COLUMNS = pd.Series([LABEL_MAP[pair] for pair in LABEL_MAP]).unique()

def load_raw_data(json_path):
    return json.load(open(json_path))

def sanitize_null_field(text):
    if pd.isnull(text) or len(text.strip()) == 0 or text == "N/A":
        return ""
    return text.strip()

def add_meta_fields():
    meta_fields = {
        "meta_organization": "UNIDO",
        "meta_category": "Technology Offer",
        "meta_collected_date": datetime.now().strftime("%m/%d/%Y %H:%M:%S")
    }
    return meta_fields

def add_description(article):
    return article["applications"] + " Area: " + article["registered_category"]

def sanitize_data(raw_data):
    labeled_data = []
    for article in raw_data:
        new_article = {}
        for key in article.keys():
            if key in LABEL_MAP:
                new_article[LABEL_MAP[key]] = sanitize_null_field(article[key])
        new_article["description"] = add_description(new_article)
        new_article.update(add_meta_fields())
        labeled_data.append(new_article)
    return labeled_data

def standardize_data(article):
    missing_cols = set(COLUMNS) - set(article.keys())
    for item in missing_cols:
        article[item] = ""
    return article

def run(read_path="data/raw_article_content.json", write_path="data/clean_article_content.json"):
    data = load_raw_data(read_path)
    sanitized_data = sanitize_data(data)
    standardized_data = [standardize_data(article) for article in sanitized_data]
    with open(write_path, "w") as f:
        json.dump(standardized_data, f)
    return standardized_data
