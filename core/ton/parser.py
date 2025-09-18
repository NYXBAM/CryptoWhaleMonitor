import logging
import requests
import time
from decimal import Decimal
from typing import Optional, List
from tonsdk.utils import Address

from config import TON_API_URL, TON_WHALE_THRESHOLD
from models.dataclass import Transaction



logger = logging.getLogger("CryptoWhaleMonitor")

class TonParser:
    """Try to parse TON transactions from the TON API and detect whale transactions."""
    API_URL = TON_API_URL
    MIN_AMOUNT = Decimal(TON_WHALE_THRESHOLD)  # 1_000_000_000 = 1 TON
    TON = Decimal("1_000000000")  # 1 TON
    
    def __init__(self):
        self.latest_lt = 0
        self.processed_txs = set() 

    def ton_addr(self, raw_addr):
        """Convert to human-readable address"""
        try:
            return Address(raw_addr).to_string(True)
        except Exception:
            return raw_addr  

    def fetch_new_txs(self, from_lt):
        """Fetch new transactions from the TON API"""
        r = requests.get(self.API_URL)
        r.raise_for_status()
        txs = r.json()["transactions"]
        return [tx for tx in txs if int(tx["lt"]) > from_lt]

    def process_whales(self, txs: List[dict]) -> List[Transaction]:
        whales = []
        EXCLUDED_ADDRESS = "Uf8zMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMxYA"

        for tx in txs:
            tx_lt = int(tx["lt"])
            if tx_lt > self.latest_lt:
                self.latest_lt = tx_lt

            desc = tx.get("description", {})
            action = desc.get("action", {})
            tx_type = desc.get("type", "")

            if not action.get("success", False):
                continue
            if tx_type == "tick_tock":
                continue

            tx_hash = tx["hash"]
            if tx_hash in self.processed_txs:
                continue  

            in_msg = tx.get("in_msg")
            if in_msg:
                val = Decimal(in_msg.get("value", "0") or "0")
                src = in_msg.get("source")
                dest = in_msg.get("destination")
                if (val >= self.MIN_AMOUNT and 
                    src and dest and src != dest and 
                    self.ton_addr(src) != EXCLUDED_ADDRESS and 
                    self.ton_addr(dest) != EXCLUDED_ADDRESS):
                    whales.append(Transaction(
                        blockchain="TON",
                        amount=float(val / self.TON),
                        amount_usd=None,  
                        id=tx_hash,
                        classification="unknown", # todo
                        link=f"https://tonscan.org/tx/{tx_hash}",
                        hash=tx_hash,
                        from_a=self.ton_addr(src),
                        to=self.ton_addr(dest),
                        value=float(val),
                        block_number=tx_lt,
                        block_hash=None
                    ))
                    self.processed_txs.add(tx_hash)
            # DEBUGGING 
            # out_msgs
            # for out in tx.get("out_msgs", []):
            #     val = Decimal(out.get("value", "0") or "0")
            #     src = tx.get("account")
            #     dest = out.get("destination")
            #     if (val >= self.MIN_AMOUNT and 
            #         tx_hash not in self.processed_txs and 
            #         src and dest and src != dest and 
            #         self.ton_addr(src) != EXCLUDED_ADDRESS and 
            #         self.ton_addr(dest) != EXCLUDED_ADDRESS):
            #         whales.append(Transaction(
            #             blockchain="TON",
            #             amount=float(val / self.TON),
            #             amount_usd=None, 
            #             id=tx_hash,
            #             classification="Unknown", # todo
            #             link=f"https://tonscan.org/tx/{tx_hash}",
            #             hash=tx_hash,
            #             from_a=self.ton_addr(src),
            #             to=self.ton_addr(dest),
            #             value=float(val),
            #             block_number=tx_lt,
            #             block_hash=None
            #         ))
            #         self.processed_txs.add(tx_hash)

        return whales
       