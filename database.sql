CREATE DATABASE IF NOT EXISTS shopify_insights;
USE shopify_insights;

-- Brands table
CREATE TABLE brands (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    website_url VARCHAR(512) NOT NULL UNIQUE,
    domain VARCHAR(255) NOT NULL,
    brand_context TEXT,
    contact_email VARCHAR(255),
    contact_phone VARCHAR(50),
    social_handles JSON,
    privacy_policy_url VARCHAR(512),
    privacy_policy_text TEXT,
    return_policy_url VARCHAR(512),
    return_policy_text TEXT,
    refund_policy_url VARCHAR(512),
    refund_policy_text TEXT,
    faqs JSON,
    important_links JSON,
    hero_products JSON,
    is_shopify_store BOOLEAN DEFAULT FALSE,
    last_scraped DATETIME,
    scraping_status VARCHAR(50) DEFAULT 'pending',
    scraping_errors TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_domain (domain),
    INDEX idx_status (scraping_status)
);

-- Products table
CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    brand_id INT NOT NULL,
    shopify_id VARCHAR(50),
    handle VARCHAR(255),
    title VARCHAR(512) NOT NULL,
    description TEXT,
    vendor VARCHAR(255),
    product_type VARCHAR(255),
    tags JSON,
    price DECIMAL(10, 2),
    compare_at_price DECIMAL(10, 2),
    product_url VARCHAR(512),
    image_urls JSON,
    featured_image VARCHAR(512),
    available BOOLEAN DEFAULT TRUE,
    inventory_quantity INT,
    variants JSON,
    seo_title VARCHAR(255),
    seo_description TEXT,
    is_hero_product BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (brand_id) REFERENCES brands(id) ON DELETE CASCADE,
    INDEX idx_brand_id (brand_id),
    INDEX idx_shopify_id (shopify_id),
    INDEX idx_product_type (product_type)
);

-- Competitors table
CREATE TABLE competitors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    brand_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    website_url VARCHAR(512) NOT NULL,
    domain VARCHAR(255) NOT NULL,
    brand_context TEXT,
    contact_email VARCHAR(255),
    contact_phone VARCHAR(50),
    social_handles JSON,
    privacy_policy_url VARCHAR(512),
    privacy_policy_text TEXT,
    return_policy_url VARCHAR(512),
    return_policy_text TEXT,
    refund_policy_url VARCHAR(512),
    refund_policy_text TEXT,
    faqs JSON,
    important_links JSON,
    hero_products JSON,
    estimated_revenue VARCHAR(100),
    market_position VARCHAR(100),
    is_shopify_store BOOLEAN DEFAULT FALSE,
    last_scraped DATETIME,
    scraping_status VARCHAR(50) DEFAULT 'pending',
    scraping_errors TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (brand_id) REFERENCES brands(id) ON DELETE CASCADE,
    INDEX idx_brand_id (brand_id),
    INDEX idx_domain (domain)
);

-- Analyses table
CREATE TABLE analyses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    brand_id INT NOT NULL,
    analysis_type VARCHAR(100) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    results JSON,
    insights JSON,
    recommendations JSON,
    analysis_status VARCHAR(50) DEFAULT 'pending',
    processing_time INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (brand_id) REFERENCES brands(id) ON DELETE CASCADE,
    INDEX idx_brand_id (brand_id),
    INDEX idx_analysis_type (analysis_type)
);