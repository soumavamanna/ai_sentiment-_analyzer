from sqlalchemy import *
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Article(Base):

    __tablename__ = "articles"

    article_id = Column(
        String,
        primary_key=True
    )

    title = Column(Text)

    content = Column(Text)

    source = Column(Text)

    url = Column(Text)

    published_at = Column(DateTime)

class MarketPrice(Base):

    __tablename__ = "market_prices"

    id = Column(
        Integer,
        primary_key=True
    )

    ticker = Column(String)

    date = Column(Date)

    open = Column(Float)

    high = Column(Float)

    low = Column(Float)

    close = Column(Float)

    volume = Column(BigInteger)