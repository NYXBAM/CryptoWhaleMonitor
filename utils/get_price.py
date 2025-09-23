import logging
import requests


from functools import wraps

logger = logging.getLogger("CryptoPriceClient")


class CryptoPriceClient:
    """"Getting crypro price from binance API"""
    BASE_URL = 'https://api.binance.com/api/v3/ticker/price'

    @staticmethod
    def get_price(symbol: str, vs_currency: str = "USDT") -> float:
        try:
            if symbol == "USDT" or symbol == "USDC":
                return 1
            pair = f"{symbol.upper()}{vs_currency.upper()}"
            url = f"{CryptoPriceClient.BASE_URL}?symbol={pair}"
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            return float(data["price"])
        except Exception as e:
            logger.error(f"Error {e}")
