from core.btc.monitor import *
from core.eth.monitor import * 

from core.btc.parser import *
from core.eth.parser import *


from config import BTC_WHALE_THRESHOLD, ETH_WHALE_THRESHOLD
import time

from data.db import engine, Base
from data.models import WhaleTransaction
from data.utils import save_whale_txs


Base.metadata.create_all(bind=engine)

def main():
    btc_parser = BitcoinParser()
    eth_parser = EthParser(whale_threshold=ETH_WHALE_THRESHOLD)


    last_btc_block = None
    last_eth_block = None


    while True:
        # ---------- BTC ----------
        try:
            latest_btc_block = btc_parser.get_btc_latest_block_hash()
            if latest_btc_block != last_btc_block:
                whales = btc_parser.parse_block(latest_btc_block)
                for tx in whales:
                    print(f"🚨 BTC whale: {tx['amount']:.2f} BTC, Tx {tx['txid']} , from {tx['from']} → {tx['to']}")
                    save_whale_txs("BTC", whales)
                last_btc_block = latest_btc_block
        except Exception as e:
            print("BTC error:", e)

        # ---------- ETH ----------
        try:
            latest_eth_block = eth_parser.get_latest_block_number()
            if latest_eth_block != last_eth_block:
                whales = eth_parser.parse_block(latest_eth_block)
                for tx in whales:
                    print(f"🚨 ETH whale: {tx['value']:.2f} ETH, Tx {tx['hash']} , from {tx['from']} → {tx['to']}")
                    save_whale_txs("ETH", whales)
                last_eth_block = latest_eth_block
        except Exception as e:
            print("ETH error:", e)

        
        time.sleep(5)  
        

if __name__ == "__main__":
    main()
