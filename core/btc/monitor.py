import requests
from config import BTC_API_URL 

class BitcoinMonitor():
    '''Class to monitor Bitcoin blockchain using aAPI'''
    def __init__(self, api_url=BTC_API_URL):
        self.BTC_API_URL = api_url
    
    
    def get_btc_latest_block_hash(self):
        return requests.get(f"{self.BTC_API_URL}/blocks/tip/hash").text

    def get_btc_block_txs(self,block_hash):
        return requests.get(f"{self.BTC_API_URL}/block/{block_hash}/txs").json()


    @staticmethod
    def satoshi_to_btc(sat):
        return sat / 1e8
