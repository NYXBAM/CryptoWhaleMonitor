# config
API = True # Enable API server  


XRPL_WS = "wss://xrplcluster.com"
XRP_SCAN_API = "https://api.xrpscan.com/api/v1/tx/"
XRP_PRICE_URL = "https://api.coingecko.com/api/v3/simple/price?ids=ripple&vs_currencies=usd"
ETH_RPC_URL = "https://ethereum-rpc.publicnode.com"
BTC_API_URL = "https://mempool.space/api"
TON_API_URL = "https://toncenter.com/api/v3/transactions"

DATABASE_URL = 'sqlite:///./whale.db'

ETH_WHALE_THRESHOLD = 500 # ETH
BTC_WHALE_THRESHOLD = 50
XRP_THRESHOLD_USD = 2_000_000 # in $USD  
TON_WHALE_THRESHOLD = 10_000  # 10000 TON in TON


# REPORT LANGUAGE
REPORT_LANGUAGE = "EN"  # or RU 

KNOWN_EXCHANGES = [
    "Binance", "Coinbase", "Kraken", "Bitfinex", "Bitstamp",
    "Huobi", "OKX", "Gemini", "Bitget", "FTX", "KuCoin", "Poloniex",
    "Wintermute", "Bybit", 'Crypto.com', "Bittrex", "Gate.io", "Upbit", "Whitebit", "BingX","Coinbase", "BitMart", "Luno", "WazirX", "ZB.com", "BitFlyer"
]
