CREATE TABLE IF NOT EXISTS articles (
    article_id BIGINT PRIMARY KEY,
    product_code BIGINT,
    prod_name TEXT,
    product_type_no INT,
    product_type_name TEXT,
    product_group_name TEXT,
    graphical_appearance_no INT,
    graphical_appearance_name TEXT,
    colour_group_code INT,
    colour_group_name TEXT,
    perceived_colour_value_id INT,
    perceived_colour_value_name TEXT,
    perceived_colour_master_id INT,
    perceived_colour_master_name TEXT,
    department_no INT,
    department_name TEXT,
    index_code TEXT,
    index_name TEXT,
    index_group_no INT,
    index_group_name TEXT,
    section_no INT,
    section_name TEXT,
    garment_group_no INT,
    garment_group_name TEXT,
    detail_desc TEXT
);

CREATE TABLE IF NOT EXISTS customers (
    customer_id TEXT PRIMARY KEY,
    FN BOOLEAN,
    Active BOOLEAN,
    club_member_status TEXT,
    fashion_news_frequency TEXT,
    age INT,
    postal_code TEXT
);