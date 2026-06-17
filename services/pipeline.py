from services.ticker_resolver import TickerResolver
from services.sentiment_engine import FinancialNLP
from services.novelty_detector import NoveltyDetector
from utils.credibility_scorer import get_credibility_score
from services.text_utils import extract_company_context
from services.impact_scorer import compute_impact
from database.repositories.market_context_repo import get_market_context
from services.technical_score import compute_technical_score
from services.signal_fusion import calculate_signal_strength

class FinancialSignalPipeline:
    def __init__(self):
        self.resolver = TickerResolver()
        self.nlp = FinancialNLP()
        self.novelty = NoveltyDetector()

    def process_article(self, raw_article: dict) -> list[dict]:
        """
        Input format example:
        {
            "id": "art_001",
            "source": "https://www.moneycontrol.com/... ",
            "text": "Reliance Industries planning massive green hydrogen push."
        }
        """
        # Step 1: Source Credibility
        cred_score = get_credibility_score(raw_article["source"])
        
        # Step 2: Ticker Resolution
        matched_companies = self.resolver.extract_ticker_info(raw_article["text"])
        
        # If no listed NSE companies are mentioned, skip or store as macro news
        if not matched_companies:
            return []

        structured_signals = []

        for company in matched_companies:

            company_text = extract_company_context(
                raw_article["text"],
                company["company_name"]
            )

            sentiment_data = self.nlp.get_sentiment(
                company_text
            )

            event_data = self.nlp.classify_event(
                raw_article["text"]
            )

            ticker = company["ticker"]
            # Step 4: Novelty Detection & Vector Insertion
            novelty_score = self.novelty.calculate_and_store_novelty(
                article_id=raw_article["id"],
                ticker=ticker,
                text=raw_article["text"]
            )
            label = sentiment_data["sentiment"].lower()

            sentiment_sign = {
                "positive": 1,
                "negative": -1,
                "neutral": 0
            }.get(label, 0)
            weighted_sentiment_score = round(
            sentiment_sign
            * sentiment_data["confidence"]
            * cred_score,
            4)
            impact_score = compute_impact(
                event_data["event_type"],
                event_data["confidence"]
            )
            market_context = get_market_context(
                company["ticker"]
            )

            technical_score = compute_technical_score(
                market_context,
                weighted_sentiment_score
            )
            signal_strength = calculate_signal_strength(

                sentiment_score=
                    abs(weighted_sentiment_score),

                novelty_score=
                    novelty_score,

                impact_score=
                    impact_score,

                event_confidence=
                    max(event_data["confidence"], 0.25),

                technical_score=
                    technical_score
            )
            
            # Step 5: Construct Final Payload
            signal = {
                "article_id": raw_article["id"],
                "ticker": ticker,
                "company_name": company["company_name"],
                "sentiment": sentiment_data["sentiment"],
                "sentiment_confidence": sentiment_data["confidence"],
                "weighted_sentiment_score": weighted_sentiment_score,
                "signal_strength": signal_strength,
                "event_type": event_data["event_type"],
                "event_confidence": event_data["confidence"],
                "novelty_score": novelty_score,
                "impact_score": impact_score,
                "source_credibility": cred_score
            }
            structured_signals.append(signal)
        return structured_signals