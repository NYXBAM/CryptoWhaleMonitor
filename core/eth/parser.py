# core/eth/parser.py
from config import ETH_WHALE_THRESHOLD, KNOWN_EXCHANGES
from models.dataclass import Transaction
from .monitor import EthMonitor
import requests
import os
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger("CryptoWhaleMonitor")

class EthParser(EthMonitor):
    '''Class to parse Ethereum blocks and identify whale transactions'''
    def __init__(self, whale_threshold=ETH_WHALE_THRESHOLD):
        super().__init__()
        self.whale_threshold = whale_threshold
        self.API_KEY = os.getenv("MORALIS_API_KEY")

    def parse_block(self, block_number):
        block_data = self.get_block(block_number)
        whales = []

        for tx in block_data["transactions"]:
            value_eth = self.wei_to_eth(tx["value"])
            if value_eth >= self.whale_threshold:
                tx_hash = tx["hash"]
                classification = self.check_tx(tx_hash)
                whales.append(Transaction( 
                    amount=value_eth, 
                    hash=tx_hash,
                    from_a=tx["from"],
                    to=tx["to"],
                    value=value_eth,
                    block_number=block_number,     
                    block_hash=block_data['hash'], 
                    classification=classification,
                ))

        return whales
    
    
    
    def check_tx(self, tx_hash):
        url = f"https://deep-index.moralis.io/api/v2.2/transaction/{tx_hash}"
        headers = {"X-API-Key": self.API_KEY}
        params = {"chain": 'eth'}

        resp = requests.get(url, headers=headers, params=params)

        if resp.status_code != 200:
            logging.error(f"Error fetching tx {tx_hash}: {resp.status_code}")
            return

        tx = resp.json()

        from_addr = tx.get("from_address")
        from_lbl  = tx.get("from_address_label")
        to_addr   = tx.get("to_address")
        to_lbl    = tx.get("to_address_label")
        # debug # 
        # print(f"Tx {tx_hash}")
        # print(f"From: {from_addr} ({from_lbl})")
        # print(f"To:   {to_addr} ({to_lbl})")
        ###########

        if from_lbl:
            for exch in KNOWN_EXCHANGES:
                if exch in from_lbl:
                    return f"withdrawal from: {from_lbl}"
     
        if to_lbl:
            for exch in KNOWN_EXCHANGES:
                if exch in to_lbl:
                    return f"deposit to: {to_lbl}"

        return "normal"

            