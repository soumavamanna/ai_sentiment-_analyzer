from services.ticker_resolver import TickerResolver
from database.repositories.social_repo import get_unprocessed_social_posts
from database.repositories.financial_signal_repo import save_financial_signals
from utils.credibility_scorer import get_credibility_score
from services.model_manager import get_nlp_engine, get_novelty_detector
from services.signal_fusion import calculate_composite_score
class SocialProcessor:
    def __init__(self):
        self.nlp = get_nlp_engine()
        self.resolver = TickerResolver()
        self.novelty = get_novelty_detector()

    def process(self):
        posts = get_unprocessed_social_posts()
        
        if not posts:
            print("No new social posts require processing.")
            return

        signals_to_save = []

        for post in posts:
            # Match the actual column names from your database schema
            text_content = post["text"]
            post_id = post["post_id"]

            companies = self.resolver.extract_ticker_info(text_content)
            if not companies:
                continue

            sentiment = self.nlp.get_sentiment(text_content)
            
            for company in companies:
                ticker = company["ticker"]

                novelty_score = self.novelty.calculate_and_store_novelty(
                    article_id=f"soc_{post_id}_{ticker}",
                    ticker=ticker,
                    text=text_content
                )

                # Base credibility on the platform it was scraped from
                credibility_score = get_credibility_score(post.get("platform", "tradingqna.com"))

                # Convert string sentiment to mathematical signs
                sentiment_sign = {"positive": 1, "negative": -1, "neutral": 0}.get(sentiment["sentiment"].lower(), 0)
                raw_sentiment_score = sentiment_sign * sentiment["confidence"]
                weighted_score = round(raw_sentiment_score * credibility_score, 4)

                # Generate a baseline composite score for social chatter
                composite_score = calculate_composite_score(
                    sentiment_score=raw_sentiment_score,
                    event_strength=0.5, # Baseline strength for social chatter
                    volume_ratio=1.0,   # Neutral fallback
                    return_20d=0.0,     # Neutral fallback
                    novelty_score=novelty_score,
                    source_credibility=credibility_score
                )

                signals_to_save.append({
                    "article_id": post_id, 
                    "ticker": ticker,
                    "sentiment": sentiment["sentiment"],
                    "sentiment_confidence": sentiment["confidence"],
                    "weighted_sentiment_score": weighted_score,
                    "event_type": "social_chatter",
                    "event_confidence": 1.0,
                    "novelty_score": novelty_score,
                    "source_credibility": credibility_score,
                    "composite_score": composite_score,
                    "explanation": f"Retail sentiment discussion detected on {post['platform']}."
                })

        if signals_to_save:
            # Use the correct plural repository function
            save_financial_signals(signals_to_save)
            print(f"✅ Processed and saved {len(signals_to_save)} social signals to PostgreSQL.")