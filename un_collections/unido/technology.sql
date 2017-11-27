CREATE TABLE IF NOT EXISTS technology(
    meta_organization TEXT NOT NULL,
    meta_category TEXT NOT NULL,
    meta_collected_date TEXT NOT NULL,
    meta_base_url TEXT NOT NULL, -- *
    title TEXT NOT NULL, -- *
    description TEXT, -- Registered category + Conceivable applications *
    sector TEXT, -- ?
    registered_category TEXT, -- Registered Category *
    features_and_advantages TEXT, -- Major Features and Advantages *
    -- applications TEXT, -- Conceivable applications *
    competitive_advantage TEXT, -- Competitive advantage *
    performance TEXT, -- Performance *
    technical_maturity TEXT, -- Technical maturity *
    risk TEXT, -- Conceivable risk *
    patent_info TEXT, -- Information on patent related to this technology *
    company_name TEXT, -- *
    company_address TEXT, -- *
    company_capital TEXT, -- *
    company_contact TEXT, -- *
    company_num_employees TEXT, -- *
    company_founded_date TEXT, -- *
    company_business_type TEXT, -- *
    modality_of_transaction TEXT -- Modality of business transaction *
);
