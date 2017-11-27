CREATE TABLE IF NOT EXISTS climate_tech_project(
    meta_organization TEXT NOT NULL,
    meta_category TEXT NOT NULL,
    meta_collected_date TEXT NOT NULL,
    meta_base_url TEXT NOT NULL,
    title TEXT NOT NULL,
    seeking_support BOOLEAN,
    project_type TEXT,
    date_posted TEXT,
    country TEXT,
    region TEXT,
    document_url TEXT,
    keywords TEXT,
    sectors TEXT
);
