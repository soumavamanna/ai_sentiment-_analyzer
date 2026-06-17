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

    __table_args__ = (
        UniqueConstraint(
            "ticker",
            "market_date",
            name="uq_ticker_date"
        ),
    )

    id = Column(
        Integer,
        primary_key=True
    )

    ticker = Column(
        String,
        nullable=False,
        index=True
    )

    market_date = Column(
        Date,
        nullable=False,
        index=True
    )

    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)

    volume = Column(BigInteger)

    return_1d = Column(Float)
    return_5d = Column(Float)
    return_20d = Column(Float)

    volatility_20d = Column(Float)

    rsi_14 = Column(Float)

    atr_14 = Column(Float)

    volume_ratio = Column(Float)

    gap_pct = Column(Float)

    relative_strength = Column(Float)

    dollar_volume = Column(Float)

    volume_surge = Column(Float)