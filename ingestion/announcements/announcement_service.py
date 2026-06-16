from ingestion.announcements.nse_collector import NSECollector
from database.repositories.announcement_repo import save_announcements

class AnnouncementService:
    def __init__(self):
        self.nse = NSECollector()

    async def collect(self):
        """Triggers the asynchronous data pipeline to monitor current NSE corporate filings."""
        data = []

        print("Fetching NSE market-wide announcements...")
        try:
            # FIX: Added 'await' keyword to pull results smoothly from our async collector
            nse_data = await self.nse.fetch_announcements()
            data.extend(nse_data)
            print(f"Added {len(nse_data)} NSE announcements.")

        except Exception as e:
            print(f"Failed to collect NSE data: {e}")
       
        if data:
            # Commit the rows to the database
            save_announcements(data)

        print(f"\nCollection Complete! Total combined announcements: {len(data)}")
        return data