import psycopg2
from psycopg2.extras import execute_batch
import os
from dotenv import load_dotenv

load_dotenv(override=True)

class DatabaseManager:
    def __init__(self):
        # Set this environment variable locally, or fallback to default local postgres
        self.db_url = os.getenv(
            "DB_URL"
            
        )
        self.init_db()

    def _get_connection(self):
        """Returns a new connection to the PostgreSQL database."""
        return psycopg2.connect(self.db_url)

    def init_db(self):
        """Initializes the schema and required performance indexes for PostgreSQL."""
        schema_query = """
        CREATE TABLE IF NOT EXISTS financial_signals (
            signal_id SERIAL PRIMARY KEY,
            article_id TEXT NOT NULL,
            ticker TEXT NOT NULL,
            sentiment TEXT NOT NULL,
            sentiment_confidence REAL NOT NULL,
            weighted_sentiment_score REAL NOT NULL,
            event_type TEXT,
            event_confidence REAL,
            novelty_score REAL NOT NULL,
            source_credibility REAL NOT NULL,
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX IF NOT EXISTS idx_signals_ticker ON financial_signals(ticker);
        CREATE INDEX IF NOT EXISTS idx_signals_processed ON financial_signals(processed_at);
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(schema_query)
                conn.commit()
        except Exception as e:
            print(f"PostgreSQL Initialization Error: {e}")

    def insert_signals(self, signals: list[dict]):
        """Inserts multiple signal records safely using a batch transaction."""
        if not signals:
            return

        # PostgreSQL uses %(key)s syntax for dictionary injection
        insert_query = """
        INSERT INTO financial_signals (
            article_id, ticker, sentiment, sentiment_confidence, 
            weighted_sentiment_score, event_type, event_confidence, 
            novelty_score, source_credibility
        ) VALUES (
            %(article_id)s, %(ticker)s, %(sentiment)s, %(sentiment_confidence)s, 
            %(weighted_sentiment_score)s, %(event_type)s, %(event_confidence)s, 
            %(novelty_score)s, %(source_credibility)s
        );
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    execute_batch(cur, insert_query, signals)
                conn.commit()
        except Exception as e:
            print(f"PostgreSQL Insert Error: {e}")