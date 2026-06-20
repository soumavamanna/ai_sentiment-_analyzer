from datetime import datetime, timedelta
from services.model_manager import get_novelty_detector
from config.logging_config import get_logger

logger = get_logger(__name__)

class SystemScheduler:
    def __init__(self):
        # Set the first ChromaDB cleanup to run immediately on script startup
        self.next_cleanup_time = datetime.now()
        self.novelty_detector = get_novelty_detector()

    def run_pending_tasks(self):
        """Checks the clock and executes any tasks that are due."""
        print("\n[4/4] System Maintenance Check...")
        
        if datetime.now() >= self.next_cleanup_time:
            print(" 🧹 Running daily ChromaDB vector cleanup...")
            
            try:
                self.novelty_detector.cleanup_old_vectors(days=30) 
                self.next_cleanup_time = datetime.now() + timedelta(days=1)
                print(f" ✅ Cleanup complete. Next run at: {self.next_cleanup_time.strftime('%Y-%m-%d %H:%M:%S')}")
            except Exception as e:
                print(f" ❌ Maintenance task failed: {e}")
                # Retry in 1 hour if it fails, rather than waiting a full day
                self.next_cleanup_time = datetime.now() + timedelta(hours=1)
        else:
            print(f" ⏳ Next DB cleanup scheduled for: {self.next_cleanup_time.strftime('%Y-%m-%d %H:%M:%S')}")