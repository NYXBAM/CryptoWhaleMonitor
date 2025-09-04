from models.dataclass import Transaction
from .monitor import BitcoinMonitor
from config import BTC_WHALE_THRESHOLD, KNOWN_EXCHANGES
import requests
from typing import List, Dict



class BitcoinWhaleParser:
    ''' Class to parse crypto whale transactions from Whale-alert.io, and
        returns list of whale transactions today. 
    '''
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
                try:
                    transaction = Transaction(
                        blockchain=amt.get("symbol"),
                        amount=amt.get("amount", 0),
                        amount_usd=amt.get("value_usd"),
                        id=item.get("id"),
                        classification=item.get("text"),
                        link = f"https://whale-alert.io/alert_click/{item.get('link')}"
                    )
                    alerts.append(transaction)
                except (ValueError, TypeError) as e:
                    print(f"Error in parser btc: {e}")
                    continue
        
        return alerts
