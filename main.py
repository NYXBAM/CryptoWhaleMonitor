# import requests
# import time

# # ========================
# # Параметри
# # ========================
# ETH_RPC_URL = "https://ethereum-rpc.publicnode.com"
# POLYGON_RPC_URL = "https://polygon-rpc.com"
# BTC_API_URL = "https://blockstream.info/api"

# ETH_WHALE_THRESHOLD = 100     # ETH
# POLYGON_WHALE_THRESHOLD = 10000 # MATIC
# BTC_WHALE_THRESHOLD = 10      # BTC

# SLEEP_ETH_POLYGON = 2  # сек
# SLEEP_BTC = 60         # сек

# # ========================
# # Функції JSON-RPC для ETH/Polygon
# # ========================
# def rpc_call(url, method, params=[]):
#     payload = {"jsonrpc":"2.0","method":method,"params":params,"id":1}
#     r = requests.post(url, json=payload)
#     r.raise_for_status()
#     return r.json()["result"]

# def get_latest_block_number(url):
#     block_hex = rpc_call(url, "eth_blockNumber")
#     return int(block_hex, 16)

# def get_block(url, block_number):
#     return rpc_call(url, "eth_getBlockByNumber", [hex(block_number), True])

# def wei_to_eth(wei):
#     return int(wei, 16) / 1e18

# # ========================
# # Функції для BTC
# # ========================
# def get_btc_latest_block_hash():
#     return requests.get(f"{BTC_API_URL}/blocks/tip/hash").text

# def get_btc_block_txs(block_hash):
#     return requests.get(f"{BTC_API_URL}/block/{block_hash}/txs").json()

# def satoshi_to_btc(sat):
#     return sat / 1e8

# # ========================
# # Головна функція
# # ========================
# if __name__ == "__main__":
#     print("🐋 Стартуємо моніторинг кит-транзакцій на ETH, Polygon і BTC...\n")

#     eth_last_block = get_latest_block_number(ETH_RPC_URL)
#     polygon_last_block = get_latest_block_number(POLYGON_RPC_URL)
#     btc_last_block_hash = get_btc_latest_block_hash()

#     while True:
#         # ----- ETH -----
#         latest_eth_block = get_latest_block_number(ETH_RPC_URL)
#         if latest_eth_block > eth_last_block:
#             for b in range(eth_last_block + 1, latest_eth_block + 1):
#                 block_data = get_block(ETH_RPC_URL, b)
#                 for tx in block_data["transactions"]:
#                     value_eth = wei_to_eth(tx["value"])
#                     if value_eth >= ETH_WHALE_THRESHOLD:
#                         print(f"🚨 ETH КИТ: {value_eth:.2f} ETH, Tx {tx['hash']}..., Блок {b}")
#             eth_last_block = latest_eth_block

#         # ----- Polygon -----
#         latest_polygon_block = get_latest_block_number(POLYGON_RPC_URL)
#         if latest_polygon_block > polygon_last_block:
#             for b in range(polygon_last_block + 1, latest_polygon_block + 1):
#                 block_data = get_block(POLYGON_RPC_URL, b)
#                 for tx in block_data["transactions"]:
#                     value_matic = wei_to_eth(tx["value"])
#                     if value_matic >= POLYGON_WHALE_THRESHOLD:
#                         print(f"🚨 Polygon КИТ: {value_matic:.2f} MATIC, Tx {tx['hash'][:10]}..., Блок {b}")
#             polygon_last_block = latest_polygon_block

#         # ----- BTC -----
#         latest_btc_block_hash = get_btc_latest_block_hash()
#         if latest_btc_block_hash != btc_last_block_hash:
#             txs = get_btc_block_txs(latest_btc_block_hash)
#             for tx in txs:
#                 total_satoshi = sum(v['value'] for v in tx['vout'])
#                 total_btc = satoshi_to_btc(total_satoshi)
#                 if total_btc >= BTC_WHALE_THRESHOLD:
#                     print(f"🚨 BTC КИТ: {total_btc:.2f} BTC, Tx {tx['txid']}")
#             btc_last_block_hash = latest_btc_block_hash

#         time.sleep(2)  # ETH + Polygon блоки ≈2 сек, BTC перевірка теж буде кожні 2 сек

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
