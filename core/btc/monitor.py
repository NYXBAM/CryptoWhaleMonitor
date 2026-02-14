import logging
import requests
from config import BTC_API_URL 

class BitcoinMonitor():
    '''Class to monitor Bitcoin blockchain using aAPI'''
    def __init__(self, api_url=BTC_API_URL):
        self.BTC_API_URL = api_url
    
    
    def get_btc_latest_block_hash(self):
        try:
            r = requests.get(f"{self.BTC_API_URL}/blocks/tip/hash", timeout=30)
            r.raise_for_status()
            return r.text
        except Exception as e:
            logging.error(f"Error getting latest block hash: {e}")
            return None
    
    
    def get_btc_block_txs(self, block_hash):
        try:
            r = requests.get(f"{self.BTC_API_URL}/block/{block_hash}/txs", timeout=30)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            logging.error(f"Error getting block transactions: {e}")
            return []


    @staticmethod
    def satoshi_to_btc(sat):
        return sat / 1e8
