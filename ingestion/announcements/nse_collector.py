from datetime import datetime
import hashlib
import time
from curl_cffi import requests  # The magic upgrade
from infrastructure.cache.redis_client import redis_client


class NSECollector:

    BASE_URL = "https://www.nseindia.com/api/corporate-announcements?index=equities"
    HOME_URL = "https://www.nseindia.com"
    REDIS_LAST_TS_KEY = "nse:last_timestamp"
    REDIS_ARTICLE_PREFIX = "nse:announcement:"

    def __init__(self):
        # Impersonate a real Chrome browser at the TLS/network packet level
        self.session = requests.Session(impersonate="chrome120")
        
        # Only add the specific routing header the NSE needs
        self.session.headers.update({
            "Referer": "https://www.nseindia.com/companies-listing/corporate-filings-announcements"
        })

    def _generate_id(self, symbol, subject, timestamp):
        raw = f"{symbol}|{subject}|{timestamp}"
        return hashlib.sha256(raw.encode()).hexdigest()

    def _get_nse_data(self):
        try:
            # Step 1: Hit the homepage to populate session cookies automatically
            self.session.get(self.HOME_URL, timeout=10)
            time.sleep(1.5)
            
            # Step 2: Fetch the payload
            response = self.session.get(self.BASE_URL, timeout=15)
            
            # curl_cffi doesn't use raise_for_status() in the exact same way on older versions,
            # but checking the status code manually works universally:
            if response.status_code != 200:
                print(f"Failed to fetch data, status code: {response.status_code}")
                return None
            
            json_response = response.json()
            
            if isinstance(json_response, dict) and "data" in json_response:
                return json_response["data"]
            return json_response
            
        except Exception as e:
            print(f"Network block or firewall failure from NSE: {e}")
            return None

    def fetch_announcements(self):
        data = self._get_nse_data()
        if not data:
            return []

        try:
            last_ts = redis_client.get(self.REDIS_LAST_TS_KEY)
            if isinstance(last_ts, bytes):
                last_ts = last_ts.decode('utf-8')

            newest_ts = last_ts
            results = []
            
            pending_items = []
            redis_keys = []

            for item in data:
                raw_time = item.get("an_dt")
                if not raw_time:
                    continue

                try:
                    dt_obj = datetime.strptime(raw_time, "%d-%b-%Y %H:%M:%S")
                    timestamp = dt_obj.strftime("%Y-%m-%d %H:%M:%S")
                except ValueError:
                    timestamp = raw_time 

                if last_ts and timestamp <= last_ts:
                    continue

                symbol = item.get("symbol", "UNKNOWN")
                subject = item.get("attchmntText", item.get("desc", ""))
                
                announcement_id = self._generate_id(symbol, subject, timestamp)
                redis_key = f"{self.REDIS_ARTICLE_PREFIX}{announcement_id}"

                redis_keys.append(redis_key)
                pending_items.append((redis_key, announcement_id, timestamp, item, symbol, subject))

            if not pending_items:
                return []

            with redis_client.pipeline() as read_pipe:
                for key in redis_keys:
                    read_pipe.exists(key)
                existence_results = read_pipe.execute()

            with redis_client.pipeline() as write_pipe:
                # Ensure the tuple unpacking matches the pending_items structure exactly
                for idx, (redis_key, ann_id, timestamp, item, symbol, subject) in enumerate(pending_items):
                    
                    if existence_results[idx]:
                        continue

                    announcement = {
                        "announcement_id": ann_id,
                        "exchange": "NSE",
                        "symbol": symbol,
                        "subject": subject,
                        "details": item.get("desc", ""),
                        "timestamp": timestamp,
                        "attachment_url": item.get("attchmntFile", "") 
                    }
                    results.append(announcement)

                    write_pipe.setex(redis_key, 604800, 1)

                    if newest_ts is None or timestamp > newest_ts:
                        newest_ts = timestamp

                if newest_ts and newest_ts != last_ts:
                    write_pipe.set(self.REDIS_LAST_TS_KEY, newest_ts)
                
                write_pipe.execute()

            return results

        except Exception as e:
            print(f"Processing error: {e}")
            return []