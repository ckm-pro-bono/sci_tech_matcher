CREATE TABLE IF NOT EXISTS technology_offer(
    meta_organization TEXT NOT NULL,
    meta_category TEXT NOT NULL,
    meta_collected_date TEXT NOT NULL,
    meta_base_url TEXT NOT NULL,
    sector TEXT,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    country TEXT,
    keywords TEXT,
    advantages TEXT,
    environmental_aspects TEXT,
    development_status TEXT,
    legal_protection TEXT,
    tech_specifications TEXT,
    transfer_terms TEXT,
    target_countries TEXT,
    contact_person TEXT,
    contact_address TEXT,
    contact_country TEXT,
    contact_city TEXT,
    contact_zip TEXT
);

