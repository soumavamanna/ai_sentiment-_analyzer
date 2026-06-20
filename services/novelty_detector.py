import time
import uuid
import chromadb
from sentence_transformers import SentenceTransformer

class NoveltyDetector:
    def __init__(self):
        # 1. Initialize embedding model locally
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # 2. Connect directly to the Dockerized ChromaDB exposed on your local machine
        self.client = chromadb.HttpClient(host="localhost", port=8000)
            
        # 3. Get or create the collection for articles
        self.collection = self.client.get_or_create_collection(
            name="financial_articles",
            metadata={"hnsw:space": "cosine"} # Use cosine similarity distance mapping
        )

    def calculate_and_store_novelty(self, article_id: str, ticker: str, text: str) -> float:
        """
        Compares an article against the last 30 days of text for a specific ticker.
        Returns a novelty score between 0.0 (completely identical) and 1.0 (entirely novel),
        then stores the new embedding into the database.
        """
        # Generate the embedding vector
        embedding = self.model.encode(text).tolist()
        current_timestamp = int(time.time())
        thirty_days_ago = current_timestamp - (30 * 24 * 60 * 60)

        # Query past articles strictly matching the ticker within the 30-day window
        query_results = self.collection.query(
            query_embeddings=[embedding],
            where={
                "$and": [
                    {"ticker": ticker},
                    {"timestamp": {"$gte": thirty_days_ago}}
                ]
            },
            n_results=5 # Check against the top 5 most similar historical pieces
        )

        # Default to 1.0 (100% novel) if no matching historical data exists for this ticker
        novelty_score = 1.0 

        if query_results and query_results['distances'] and len(query_results['distances'][0]) > 0:
            # ChromaDB cosine distance range is 0 to 2 (where 0 means identical).
            # We normalize the closest distance to determine visual similarity.
            smallest_distance = min(query_results['distances'][0])
            
            # Convert distance back to a standard similarity alignment
            semantic_novelty = min(smallest_distance / 2.0,1.0)
            
            # Novelty is the inverse of similarity
            novelty_score = round(semantic_novelty, 4)

        # Ensure the score stays securely within boundaries
        novelty_score = round(max(0.0, min(1.0, novelty_score)), 4)

        # Upsert the current article into ChromaDB for future tracking
        self.collection.upsert(
            ids=[article_id if article_id else str(uuid.uuid4())],
            embeddings=[embedding],
            metadatas=[{
                "ticker": ticker,
                "timestamp": current_timestamp
            }],
            documents=[text[:500]] # Store a small snippet for debugging/reference
        )

        return novelty_score
    def cleanup_old_vectors(self, days=30):
        threshold = int(time.time()) - (days * 24 * 60 * 60)
        self.collection.delete(
            where={"timestamp": {"$lt": threshold}}
        )