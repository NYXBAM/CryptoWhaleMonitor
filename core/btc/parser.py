from .monitor import BitcoinMonitor
from config import BTC_WHALE_THRESHOLD, KNOWN_EXCHANGES
import requests
from typing import List, Dict



class BitcoinWhaleParser:
    def __init__(self):
        self.url = "https://whale-alert.io/alerts.json?range=today"
    
    def fetch_whale_alerts(self):
        try:
            r = requests.get(self.url, timeout=20)
            r.raise_for_status()
        except Exception as e:
            print("Fetch error:", e)
            return []

        data = r.json()
        alerts = []

        for item in data:
            for amt in item.get("amounts", []):
                alerts.append({
                    "blockchain": amt.get("symbol"),
                    "amount": amt.get("amount"),
                    "id": item.get("id"),
                    "classification": item.get("text"),
                    "link": f"https://whale-alert.io/alert_click/{item.get('link')}"
                })
                

        return alerts
