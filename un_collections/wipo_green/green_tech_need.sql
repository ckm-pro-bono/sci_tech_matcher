CREATE TABLE IF NOT EXISTS green_tech_need(
    meta_organization TEXT NOT NULL,
    meta_category TEXT NOT NULL,
    meta_collected_date TEXT NOT NULL,
    meta_base_url TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,  
    seeking_support BOOLEAN,
    date_posted TEXT,
    last_updated TEXT,
    submitted_by TEXT,
    technical_fields TEXT
);