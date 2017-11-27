CREATE TABLE IF NOT EXISTS cittc_technology_offer(
    meta_organization TEXT NOT NULL,
    meta_category TEXT NOT NULL,
    meta_collected_date TEXT NOT NULL,
    meta_base_url TEXT NOT NULL,

    published TEXT, -- Publish
    window TEXT, -- Before
    country TEXT, -- Country
    region TEXT, -- Region

    title TEXT NOT NULL, -- title
    description TEXT NOT NULL, -- Project Description
    sector TEXT, -- sector
    secondary_field TEXT, -- Secondary Field
    technology_readiness_level TEXT, -- Technology Readiness Level
    cooperation_type TEXT, -- Mode of Co-operation
    keywords TEXT, -- Keywords

    intellectual_property_type TEXT, -- Intellectual Property
    patent_info TEXT, -- Filing / Grant No
    implementation TEXT, -- Implementation
    market_prospect TEXT, -- Market Prospect

    contact_organization TEXT, -- Name of Project Owner/Holder
    contact_organization_type TEXT, -- Organization Type
    contact_person TEXT, -- Name
    contact_employer TEXT, -- Employer
    contact_email TEXT -- E-mail Address
    contact_phone TEXT, -- Telephone
);
