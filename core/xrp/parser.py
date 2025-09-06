from config import XRPL_WS, XRP_THRESHOLD_USD, XRP_PRICE_URL
from core.xrp.monitor import XRPMonitor
from models.dataclass import Transaction

import asyncio
import json
import websockets
from decimal import Decimal
import aiohttp
from typing import List
import time
import logging

logger = logging.getLogger("CryptoWhaleMonitor")

class XRPParser:
    def __init__(self, XRP_THRESHOLD_USD=XRP_THRESHOLD_USD):
        self.THRESHOLD_USD = XRP_THRESHOLD_USD 
        self.XRP_PRICE_URL = XRP_PRICE_URL       
    
    async def get_xrp_price(self):
        try:
            url = self.XRP_PRICE_URL
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    data = await resp.json()
                    return Decimal(str(data["ripple"]["usd"]))
        except Exception as e:
            logger.error(f"Error fetching $XRP price: {e}")
    
    @classmethod
    async def listen_whales(cls):
        monitor = XRPMonitor()
        instance = cls()
        xrp_price = await instance.get_xrp_price()

        async with websockets.connect(XRPL_WS) as ws:
            await ws.send(json.dumps({
                "id": 1,
                "command": "subscribe",
                "streams": ["transactions"]
            }))

            logger.info(f"Connected to {XRPL_WS}, listening for whale transactions...")

            while True:
                try:
                    msg = await ws.recv()
                    data = json.loads(msg)
                    tx = data.get("transaction")

                    if not tx or tx.get("TransactionType") != "Payment":
                        continue
                    if tx.get("Account") == tx.get("Destination"):
                        continue

                    amount = tx.get("Amount")
                    usd_value = None
                    raw_amount = None
                    currency = "XRP"

                    if isinstance(amount, str) and amount.isdigit():
                        xrp_amount = Decimal(amount) / 1_000_000
                        usd_value = float(xrp_amount * Decimal(xrp_price))
                        raw_amount = float(xrp_amount)

                    elif isinstance(amount, dict):
                        currency = decode_currency(amount.get("currency"))
                        value_str = amount.get("value", "0") or "0"
                        value = Decimal(value_str)
                        raw_amount = float(value)

                        if currency.upper() in ["USD", "USDT", "USDC"]:
                            usd_value = float(value)

                    if usd_value and usd_value >= XRP_THRESHOLD_USD:
                        hash = tx.get('hash')
                        classification = monitor.get_address_classification(hash)

                        transaction = Transaction(
                            blockchain="XRP",
                            amount=raw_amount,
                            amount_usd=usd_value,
                            id=tx.get('hash') or '',
                            classification=classification,
                            link=f"https://xrpscan.com/tx/{tx.get('hash')}",
                            hash=tx.get('hash') or '',
                            from_a=tx.get('Account') or 'Unknown',
                            to=tx.get('Destination') or 'Unknown',
                            value=raw_amount,
                            block_number=None,
                            block_hash=None
                        )

                        logger.info("🐋 Whale Alert!")
                        yield [transaction]

                except websockets.exceptions.ConnectionClosed:
                    logger.error("WebSocket connection closed")
                    break
                except Exception as e:
                    logger.error(f"Error in $XRP parser: {e}")
                    continue

def decode_currency(currency_hex: str) -> str:
        try:
            return bytes.fromhex(currency_hex).decode("utf-8").strip("\x00")
        except Exception:
            return currency_hex
        
