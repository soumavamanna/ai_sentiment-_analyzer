import time
from curl_cffi import requests
from utils.cache_manager import CacheManager

class BSECollector:
    BASE_URL = "https://api.bseindia.com/BseIndiaAPI/api/AnnSubCategoryGetData/w"
    HOME_URL = "https://www.bseindia.com/"

    def __init__(self):
        self.session = requests.Session(impersonate="chrome120")
        self.session.headers.update({
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.bseindia.com/corporates/ann.html", 
            "Origin": "https://www.bseindia.com"
        })

    def _get_bse_data(self, scrip_code):
        try:
            self.session.get(self.HOME_URL, timeout=10)
            time.sleep(1.0)
            
            # THE FIX: Changed to a "Scrip Search"
            query_params = {
                "pageno": "1",
                "strCat": "-1",
                "strPrevDate": "",         # Leave blank for scrip search
                "strScrip": scrip_code,    # Inject the 6-digit code here!
                "strSearch": "S",          # 'S' tells BSE we are searching by Scrip
                "strToDate": "",           # Leave blank
                "strType": "C",
                "subcategory": ""          
            }
            
            response = self.session.get(
                self.BASE_URL, 
                params=query_params, 
                timeout=15
            )
            
            if response.status_code != 200:
                print(f"Failed to fetch BSE data, status code: {response.status_code}")
                return None
            
            json_response = response.json()
            
            if isinstance(json_response, dict) and "Table" in json_response:
                return json_response["Table"]
            elif isinstance(json_response, list):
                return json_response
            
            return []
            
        except Exception as e:
            print(f"Network block or firewall failure from BSE: {e}")
            return None

    def fetch_announcements(self, scrip_code):
        # 1. Pass the scrip code down to the network request
        data = self._get_bse_data(scrip_code)
        
        if not data:
            return []

        try:
            # 2. Use a unique cache key for EACH company (e.g., "bse_500325")
            cache_key = f"bse_{scrip_code}"
            last_ts = CacheManager.get_last_timestamp(cache_key)
            newest_ts = last_ts
            announcements = []

            for item in data:
                timestamp = item.get("DT_TM")
                if not timestamp:
                    continue

                if last_ts and timestamp <= last_ts:
                    continue

                headline = item.get("HEADLINE", "")
                symbol = str(item.get("SCRIP_CD", ""))

                unique_text = f"{symbol}|{headline}|{timestamp}"
                item_id = CacheManager.generate_hash(unique_text)

                if CacheManager.is_processed("bse", item_id):
                    continue

                announcements.append({
                    "announcement_id": item_id,
                    "exchange": "BSE",
                    "symbol": symbol,
                    "subject": headline,
                    "details": item.get("NEWS_SUB", ""),
                    "timestamp": timestamp,
                    "attachment_url": item.get("ATTACHMENTNAME", "") 
                })

                CacheManager.mark_processed("bse", item_id)

                if newest_ts is None or timestamp > newest_ts:
                    newest_ts = timestamp

            if newest_ts and newest_ts != last_ts:
                CacheManager.set_last_timestamp(cache_key, newest_ts)

            return announcements

        except Exception as e:
            print(f"BSE Processing Error: {e}")
            return []