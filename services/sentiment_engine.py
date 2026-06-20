from transformers import pipeline
import torch

class FinancialNLP:
    def __init__(self):
        # Set device to GPU if available, else CPU
        self.device = 0 if torch.cuda.is_available() else -1
        
        # 2.1 FinBERT Sentiment
        self.sentiment_pipe = pipeline(
            "text-classification", 
            model="ProsusAI/finbert", 
            device=self.device
        )
        
        # 2.3 Event Classification (Zero-Shot)
        self.event_pipe = pipeline(
            "zero-shot-classification", 
            model="facebook/bart-large-mnli",
            device=self.device
        )
        self.event_labels = [

            "earnings beat",
            "earnings miss",

            "guidance raise",
            "guidance cut",

            "large order win",

            "government approval",

            "regulatory action",

            "share buyback",

            "promoter buying",

            "promoter selling",

            "dividend increase",

            "dividend cut",

            "merger",

            "acquisition",

            "debt restructuring",

            "lawsuit",

            "ceo departure",

            "analyst upgrade",

            "analyst downgrade"
        ]

    def get_sentiment(self, text: str) -> dict:
        result = self.sentiment_pipe(text)[0]
        return {
            "sentiment": result["label"],
            "confidence": round(result["score"], 4)
        }

    def classify_event(self, text: str) -> dict:
        result = self.event_pipe(text, self.event_labels)
        # Return the top predicted event
        return {
            "event_type": result["labels"][0],
            "confidence": round(result["scores"][0], 4)
        }
    def sentiment_to_score(
        self,
        sentiment: str,
        confidence: float
    ):

        mapping = {
            "positive": 1,
            "negative": -1,
            "neutral": 0
        }

        return (
            mapping.get(
                sentiment.lower(),
                0
            ) * confidence
        )