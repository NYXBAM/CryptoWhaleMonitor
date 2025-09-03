from core.btc.monitor import *
from core.eth.monitor import * 

from core.btc.parser import *
from core.eth.parser import *

from utils.send_telegram_channel import send_telegram_message


from config import BTC_WHALE_THRESHOLD, ETH_WHALE_THRESHOLD
import time

from data.db import engine, Base
from data.models import WhaleTransaction
from data.utils import *


import hashlib
import json





Base.metadata.create_all(bind=engine)

def main():
    btc_whale = BitcoinWhaleParser()
    eth_parser = EthParser(whale_threshold=ETH_WHALE_THRESHOLD)

    # btc_parser = BitcoinMonitor()
    # last_btc_block = None
    last_eth_block = None

    seen_hashes = load_seen_hashes()
    alerts = []

    while True:
        try:
            # latest_btc_block = btc_parser.get_btc_latest_block_hash()
            # if latest_btc_block != last_btc_block:
            new_alerts = btc_whale.fetch_whale_alerts()
            fresh_alerts = []
            for a in new_alerts:
                alert_str = json.dumps(a, sort_keys=True)  
                alert_hash = hashlib.sha256(alert_str.encode()).hexdigest()
                if alert_hash not in seen_hashes:
                    seen_hashes.add(alert_hash)
                    fresh_alerts.append(a)
                
                if fresh_alerts:
                    save_seen_hashes(seen_hashes)
            if fresh_alerts:
                for a in fresh_alerts:
                    print(f"${a['blockchain']} whale: {a['amount']} {a['classification']}")
                
                alerts.extend(fresh_alerts)

                for a in fresh_alerts:
                    blockchain = a['blockchain']
                    amount = a['amount']
                    amount_usd = a['amount_usd']
                    classification = a['classification']
                    link = a['link']
                    message = (
                        f"🐳 <b>${blockchain} Whale-Alert.io!</b>\n\n"
                        f"💰 Amount: <b>{amount:.2f} {blockchain}</b>\n"
                        f"💵 USD Value: ${amount_usd:,.2f}\n"
                        f"🏦 Classification: {classification}\n"
                        f"🔗 Link: <a href='{link}'>View Alert</a>"
                    )
                    send_telegram_message(message)

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

        
        time.sleep(60)  
        

if __name__ == "__main__":
    main()
