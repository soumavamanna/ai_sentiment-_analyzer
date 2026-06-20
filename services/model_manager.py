from functools import lru_cache
from services.sentiment_engine import FinancialNLP
from services.novelty_detector import NoveltyDetector

@lru_cache(maxsize=1)
def get_nlp_engine():
    return FinancialNLP()

@lru_cache(maxsize=1)
def get_novelty_detector():
    return NoveltyDetector()