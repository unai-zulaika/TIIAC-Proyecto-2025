-- ===========================================================
-- Script de inicialización de la base de datos H&M
-- ===========================================================

-- Tabla: customers
CREATE TABLE IF NOT EXISTS customers (
    customer_id VARCHAR(64) PRIMARY KEY,
    FN SMALLINT,
    Active SMALLINT,
    club_member_status VARCHAR(20),
    fashion_news_frequency VARCHAR(20),
    age SMALLINT,
    postal_code VARCHAR(128)
);

-- Tabla: articles
CREATE TABLE IF NOT EXISTS articles (
    article_id BIGINT PRIMARY KEY,
    product_code INTEGER,
    prod_name VARCHAR(128),
    product_type_no INTEGER,
    product_type_name VARCHAR(64),
    product_group_name VARCHAR(64),
    graphical_appearance_no INTEGER,
    graphical_appearance_name VARCHAR(64),
    colour_group_code INTEGER,
    colour_group_name VARCHAR(64),
    perceived_colour_value_id INTEGER,
    perceived_colour_value_name VARCHAR(64),
    perceived_colour_master_id INTEGER,
    perceived_colour_master_name VARCHAR(64),
    department_no INTEGER,
    department_name VARCHAR(64),
    index_code VARCHAR(8),
    index_name VARCHAR(64),
    index_group_no INTEGER,
    index_group_name VARCHAR(64),
    section_no INTEGER,
    section_name VARCHAR(64),
    garment_group_no INTEGER,
    garment_group_name VARCHAR(64),
    detail_desc TEXT
);

-- Tabla: article_images
CREATE TABLE IF NOT EXISTS article_images (
    image_id SERIAL PRIMARY KEY,
    article_id BIGINT REFERENCES articles(article_id),
    image_path TEXT NOT NULL
);