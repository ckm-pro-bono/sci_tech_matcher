CREATE TABLE IF NOT EXISTS cittc_technology_request(
    meta_organization TEXT NOT NULL,
    meta_category TEXT NOT NULL,
    meta_collected_date TEXT NOT NULL,
    meta_base_url TEXT NOT NULL,

    published TEXT, -- Publish
    window TEXT, -- Before
    country TEXT, -- Country

    title TEXT NOT NULL, -- title
    description TEXT NOT NULL, -- Description of Demand
    sector TEXT, -- sector
    secondary_field TEXT, -- Secondary Field
    cooperation_type TEXT, -- Mode of Co-operation
    keywords TEXT, -- Keywords

    contact_organization TEXT, -- Name of Project Owner/ Holders
    contact_organization_type TEXT, -- Organization Type
    contact_person TEXT, -- Name
    contact_employer TEXT, -- Employer
    contact_email TEXT -- Email Address
    contact_phone TEXT, -- Telephone
);
