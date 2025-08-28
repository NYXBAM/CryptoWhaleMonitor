# core/eth/parser.py
from config import ETH_WHALE_THRESHOLD
from .monitor import EthMonitor

class EthParser(EthMonitor):
    '''Class to parse Ethereum blocks and identify whale transactions'''
    def __init__(self, whale_threshold=ETH_WHALE_THRESHOLD):
        super().__init__()
        self.whale_threshold = whale_threshold

    def parse_block(self, block_number):
        block_data = self.get_block(block_number)
        whales = []

        for tx in block_data["transactions"]:

            value_eth = self.wei_to_eth(tx["value"])
            if value_eth >= self.whale_threshold:
                whales.append({
                    "hash": tx["hash"],
                    "from": tx["from"],
                    "to": tx["to"],
                    "value": value_eth,
                    "block_number": block_number,     
                    "block_hash": block_data['hash'],  
                })

        return whales
