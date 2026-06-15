import pandas as pd
from ingestion.announcements.nse_collector import NSECollector
from ingestion.announcements.bse_collector import BSECollector

class AnnouncementService:

    def __init__(self, bse_metadata_path=r"D:\Scripts\ai_sentiment_analyzer\services\data\bse_company_metadata.csv"):
        self.nse = NSECollector()
        self.bse = BSECollector()
        # We store the path to your CSV file so the service can access it
        self.bse_metadata_path = bse_metadata_path

    def collect(self):
        data = []

        # ==========================================
        # 1. Collect NSE Data (Market-Wide Pull)
        # ==========================================
        print("Fetching NSE market-wide announcements...")
        try:
            nse_data = self.nse.fetch_announcements()
            data.extend(nse_data)
            print(f"Added {len(nse_data)} NSE announcements.")
        except Exception as e:
            print(f"Failed to collect NSE data: {e}")

        # ==========================================
        # 2. Collect BSE Data (Targeted CSV Pull)
        # ==========================================
        print("\nFetching BSE targeted announcements...")
        try:
            # Read the CSV to get our 6-digit Scrip Codes
            df = pd.read_csv(self.bse_metadata_path)
            bse_total_added = 0
            
            for index, row in df.iterrows():
                scrip_code = str(row["ticker"])
                company_name = row["company_name"]
                
                print(f"  -> Polling BSE for {company_name} ({scrip_code})...")
                bse_data = self.bse.fetch_announcements(scrip_code)
                
                if bse_data:
                    data.extend(bse_data)
                    bse_total_added += len(bse_data)
                    
            print(f"Added {bse_total_added} targeted BSE announcements.")

        except FileNotFoundError:
            print(f"Warning: {self.bse_metadata_path} not found. Ensure the file is in the root directory.")
        except Exception as e:
            print(f"Failed to collect targeted BSE data: {e}")

        # ==========================================
        # 3. Return the unified dataset
        # ==========================================
        print(f"\nCollection Complete! Total combined announcements: {len(data)}")
        return data