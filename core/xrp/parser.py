from config import XRPL_WS, XRP_THRESHOLD_USD
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
    
    async def get_xrp_price(self):
        try:
            url = "https://api.coingecko.com/api/v3/simple/price?ids=ripple&vs_currencies=usd"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    data = await resp.json()
                    return Decimal(str(data["ripple"]["usd"]))
        except Exception as e:
            logger.error(f"Error fetching $XRP price: {e}")
    
    @classmethod
    async def listen_whales(cls) -> List[Transaction]:
        # TODO Decorator for return whales without stoping websocket, bcs transactions in blockchain very fast 
        whales = []
        instance = cls()
        xrp_price = await instance.get_xrp_price()
        
        async with websockets.connect(XRPL_WS) as ws:
            await ws.send(json.dumps({
                "id": 1,
                "command": "subscribe", 
                "streams": ["transactions"]
            }))

            logger.info(f"Connected to {XRPL_WS}, listening for whale transactions...")

            
            start_time = time.time()
            max_duration = 60 
            max_whales = 5
            
            while time.time() - start_time < max_duration and len(whales) < max_whales:
                try:
                    try:
                        msg = await asyncio.wait_for(ws.recv(), timeout=30.0)
                    except asyncio.TimeoutError:
                        if whales or time.time() - start_time >= max_duration - 10:
                            break
                        continue

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
                        try:
                            xrp_amount = Decimal(amount) / 1_000_000
                            usd_value = float(xrp_amount * Decimal(xrp_price))
                            raw_amount = float(xrp_amount)
                            currency = "XRP"
                        except Exception as e:
                            continue

                    elif isinstance(amount, dict):
                        currency = decode_currency(amount.get("currency"))
                        value_str = amount.get("value", "0") or "0"
                        try:
                            value = Decimal(value_str)
                            raw_amount = float(value)
                            
                            if currency.upper() in ["USD", "USDT", "USDC"]:
                                usd_value = float(value)
                            else:
                                usd_value = None
                        except Exception as e:
                            continue
                    
                    if usd_value and usd_value >= XRP_THRESHOLD_USD:
                        transaction = Transaction(
                            blockchain="XRP",
                            amount=raw_amount,
                            amount_usd=usd_value,
                            id=tx.get('hash') or '',
                            classification="whale",
                            link=f"https://xrpscan.com/tx/{tx.get('hash')}",
                            hash=tx.get('hash') or '',
                            from_a=tx.get('Account') or 'Unknown',
                            to=tx.get('Destination') or 'Unknown',
                            value=raw_amount,
                            block_number=None,
                            block_hash=None
                        )
                        
                        whales.append(transaction)
                        logger.info("🐋 Whale Alert!")
                        logger.info(f"From: {transaction.from_a}")
                        logger.info(f"To: {transaction.to}")
                        logger.info(f"Amount: {transaction.amount:,.0f} {currency}")
                        logger.info(f"≈ {transaction.amount_usd:,.0f} USD")
                        logger.info(f"Link: {transaction.link}")
                        logger.info("-" * 60)

                except websockets.exceptions.ConnectionClosed:
                    logging.error("WebSocker connection closed")
                    break
                    
                except Exception as e:
                    logging.error(f"Error in $XRP parser: {e}")
                    continue
        return whales

def decode_currency(currency_hex: str) -> str:
        try:
            return bytes.fromhex(currency_hex).decode("utf-8").strip("\x00")
        except Exception:
            return currency_hex
        
