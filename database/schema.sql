CREATE TABLE IF NOT EXISTS companies (
    ticker VARCHAR(20) PRIMARY KEY,
    company_name VARCHAR(255),
    sector VARCHAR(100),
    industry VARCHAR(100),
    market_cap_category VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS articles (
    article_id VARCHAR(255) PRIMARY KEY,
    title TEXT,
    content TEXT,
    source VARCHAR(100),
    url TEXT UNIQUE,
    published_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS social_posts (
    post_id VARCHAR(255) PRIMARY KEY,
    platform VARCHAR(50),
    author VARCHAR(255),
    text TEXT,
    timestamp TIMESTAMP,
    engagement INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS market_prices (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(20),
    market_date DATE,

    open NUMERIC(15,4),
    high NUMERIC(15,4),
    low NUMERIC(15,4),
    close NUMERIC(15,4),

    volume BIGINT,

    created_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(ticker, market_date)
);
CREATE TABLE IF NOT EXISTS article_company_map (
    article_id VARCHAR(255),
    ticker VARCHAR(20),
    PRIMARY KEY(article_id, ticker)
);
CREATE TABLE IF NOT EXISTS sector_membership (

    ticker VARCHAR(20),
    sector_name VARCHAR(100),
    PRIMARY KEY(
        ticker,
        sector_name
    )
);
CREATE TABLE IF NOT EXISTS sector_signals (

    id SERIAL PRIMARY KEY,
    sector_name VARCHAR(100),
    sentiment_score FLOAT,
    article_count INTEGER,
    created_at TIMESTAMP
);
CREATE TABLE IF NOT EXISTS announcements
(
    announcement_id TEXT PRIMARY KEY,
    exchange TEXT,
    symbol TEXT,
    subject TEXT,
    details TEXT,
    timestamp TIMESTAMP,
    attachment_url TEXT
);