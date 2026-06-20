from services.ticker_resolver import TickerResolver
from services.model_manager import get_nlp_engine, get_novelty_detector
from utils.credibility_scorer import get_credibility_score
from utils.text_utils import extract_company_context
from services.impact_scorer import compute_impact
from database.repositories.market_context_repo import get_market_context

# --- NEW IMPORTS ---
from services.signal_fusion import calculate_composite_score
from services.explainability_engine import generate_explanation

class FinancialSignalPipeline:
    def __init__(self):
        self.resolver = TickerResolver()
        self.nlp = get_nlp_engine()
        self.novelty = get_novelty_detector()

    def process_article(self, raw_article: dict) -> list[dict]:
        cred_score = get_credibility_score(raw_article["source"])
        matched_companies = self.resolver.extract_ticker_info(raw_article["text"])
        
        if not matched_companies:
            return []

        structured_signals = []

        for company in matched_companies:
            ticker = company["ticker"]
            company_text = extract_company_context(raw_article["text"], company["company_name"])
            
            sentiment_data = self.nlp.get_sentiment(company_text)
            event_data = self.nlp.classify_event(raw_article["text"])
            
            novelty_score = self.novelty.calculate_and_store_novelty(
                article_id=raw_article["id"],
                ticker=ticker,
                text=raw_article["text"]
            )
            
            label = sentiment_data["sentiment"].lower()
            sentiment_sign = {"positive": 1, "negative": -1, "neutral": 0}.get(label, 0)
            
            # Base sentiment score (-1 to 1)
            raw_sentiment_score = sentiment_sign * sentiment_data["confidence"]
            
            # Get market context (returns dict with volume_ratio, return_20d, etc.)
            market_context = get_market_context(ticker) or {}
            event_strength = compute_impact(event_data["event_type"], event_data["confidence"])
            # --- PHASE 3: COMPOSITE SCORE ---
            composite_score = calculate_composite_score(
                sentiment_score=raw_sentiment_score,
                event_strength=event_strength,
                volume_ratio=market_context.get("volume_ratio", 1.0),
                return_20d=market_context.get("return_20d", 0.0),
                novelty_score=novelty_score,
                source_credibility=cred_score
            )
            
            # --- PHASE 3: EXPLAINABILITY ---
            explanation = generate_explanation(
                ticker=ticker,
                score=composite_score,
                sentiment=sentiment_data["sentiment"],
                volume_ratio=market_context.get("volume_ratio", 1.0),
                event_type=event_data["event_type"],
                novelty_score=novelty_score
            )
            weighted_sentiment_score = round(raw_sentiment_score * cred_score, 4)
            signal = {
                "article_id": raw_article["id"],
                "ticker": ticker,
                "company_name": company["company_name"],
                "sentiment": sentiment_data["sentiment"],
                "sentiment_confidence": sentiment_data["confidence"],
                "weighted_sentiment_score": weighted_sentiment_score,
                "event_type": event_data["event_type"],
                "event_confidence": event_data["confidence"],
                "novelty_score": novelty_score,
                "source_credibility": cred_score,
                "composite_score": composite_score,    # NEW
                "explanation": explanation             # NEW
            }
            structured_signals.append(signal)

        return structured_signals