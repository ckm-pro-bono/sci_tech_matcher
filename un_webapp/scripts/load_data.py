import os
import yaml
import json
import pandas as pd
import numpy as np
from main.models import Organization, Category, Content


class bcolors:
    OKGREEN = '\033[92m'
    ENDC = '\033[0m'


def read_data(org_data, data_path):
    df = pd.read_json(os.path.join(data_path, "{}.json".format(org_data)))
    return df

def read_yaml(path):
    with open(path, "r") as f:
        return yaml.load(f)

def invert_mapping(mapping):
    """
        Assumes mapping is a flat dict of form;
        {collection schema field: content model field}
        Inverts the flat dict except for cases where the value
        of the flat dict is null; preserves these.
    """
    return {val if val is not None else key: key if val is not None else val
            for key, val in mapping.items()}

def get_org_name(org_data_name):
    """Return user-friendly org name from dev / undercase names"""
    names = {'apctt_offer':'APCTT',
             'apctt_request': 'APCTT',
             'een': 'EEN',
             'unossc': 'UNOSSC',
             'wipo_green': 'WIPO Green',
             'unido': 'UNIDO',
             'unfccc': 'UNFCCC',
             'cittc_offer': 'CITTC',
             'cittc_request': 'CITTC'
    }
    return names[org_data_name]

def transform(org_data, df):
    """Switch case - perform munging for each data source"""
    if org_data == 'een':
        df['meta_collected_date'] = '2017-11-11'
        df['keywords'] = df.nace_keywords + df.technology_keywords + df.market_keywords
        df['keywords'] = df.keywords.str.replace('(\d{3,8})|([A-Z]+\.\d{1,2}(\.\d)*)', '')
        df['keywords'] = df.keywords.str.replace('\n', ',')
    
    if org_data == 'apctt_offer':
        df.rename(columns={'url': 'meta_base_url'}, inplace=True)
        df['meta_collected_date'] = '2017-11-15'
        df['meta_category'] = 'Offer'       

    if org_data == 'apctt_request':
        df.rename(columns={'url': 'meta_base_url'}, inplace=True)
        df['meta_collected_date'] = '2017-11-15'
        df['meta_category'] = 'Need'

    if org_data == 'unossc':
        df['meta_collected_date'] = pd.to_datetime(df.meta_collected_date).dt.strftime('%Y-%m-%d')

    if org_data == 'wipo_green':
        df['meta_category'] = df.meta_category.str.title()
        df['technical_fields'] = df.technical_fields.str.replace(" >|\n", ",").str.lower()
        df['meta_collected_date'] = '2017-11-15'
        df['date_posted'] = pd.to_datetime(df.date_posted).dt.strftime('%Y-%m-%d')
        df.date_posted.replace({'NaT': None}, inplace=True)
        df.benefits.fillna('', inplace=True)
        df.project_summary.fillna('', inplace=True)
        df['summary'] = df.project_summary + df.benefits

    if org_data == 'unido':
        df.drop_duplicates(['description'], inplace=True)
        df['meta_category'] = 'Offer'
        df['meta_collected_date'] = pd.to_datetime(df.meta_collected_date).dt.strftime('%Y-%m-%d')
        df['sector'] = df.title.apply(lambda x: x.split(":")[0])
        df['title'] = df.title.apply(lambda x: x.split(":")[1])
        df['country'] = 'Japan'

    if org_data == 'unfccc':
        df['meta_category'] = df.seeking_support.apply(lambda x: "Need" if x else "Publication")
        df['meta_collected_date'] = pd.to_datetime(df.meta_collected_date).dt.strftime('%Y-%m-%d')
        df['sector'] = df.sector.str.replace(" /", ",")
        df['sector'] = df.sector.apply(lambda x: x.split(",")[0])

    if org_data == 'cittc_offer':
        df.drop_duplicates(['description'], inplace=True)
        df['meta_collected_date'] = pd.to_datetime(df.meta_collected_date).dt.strftime('%Y-%m-%d')
        df['published'] = pd.to_datetime(df.published).dt.strftime('%Y-%m-%d')
        df['meta_category'] = 'Offer'
    
    if org_data == 'cittc_request':
        df.drop_duplicates(['description'], inplace=True)
        df['meta_collected_date'] = pd.to_datetime(df.meta_collected_date).dt.strftime('%Y-%m-%d')
        df['published'] = pd.to_datetime(df.published).dt.strftime('%Y-%m-%d')
        df['meta_category'] = 'Need'

    return df

def load(org_data, df, col_map):
    """Create and save Content instance for each row in df"""

    print("Loading data for {}".format(org_data))

    org_name = get_org_name(org_data)
    col_map = invert_mapping(col_map)
    org, _ = Organization.objects.get_or_create(name=org_name)

    for idx, row in df.iterrows():
        category, _ = Category.objects.get_or_create(name=row.meta_category)
        content, _ = Content.objects.update_or_create(
                          organization = org,
                          category = category,
                          collected_date = row.get(col_map['collected_date'], ''),
                          title = row.get(col_map['title'], ''),
                          description = row.get(col_map['description'], 'No description available'),
                          url = row.get(col_map['url'], ''),
                          sector = row.get(col_map['sector'], ''),
                          country = row.get(col_map['country'], ''),
                          keywords = row.get(col_map['keywords'], ''),
                          full_text = row.get(col_map['full_text'], ''),
                          date_published = row.get(col_map['date_published'], None),
                          )
        

    print(bcolors.OKGREEN + 'Loaded {} data'.format(org_data) + bcolors.ENDC)


def run():

    UN_DATA_DIR = 'data/'
    MAPPING_PATH = 'scripts/field_mapping.yaml'

    mapping = read_yaml(MAPPING_PATH)

    for org_data in mapping.keys():
        df = read_data(org_data, UN_DATA_DIR)
        df = transform(org_data, df)
        load(org_data, df, mapping[org_data])


