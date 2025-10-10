"""
Solana parser implementation

"""

from config import SOL_THRESHOLD_USD, SOL_RPC_URL
from core.sol.monitor import SolanaMonitor
from models.dataclass import Transaction

import asyncio
import aiohttp
from decimal import Decimal
import logging

from utils import get_price

logger = logging.getLogger(__name__)


LAMPORTS_PER_SOL = 1_000_000_000

# SOL block generated ~ every 0.4 sec
RETRY_DELAY = 0.2



class SolanaParser:
    def __init__(self, SOL_THRESHOLD_USD=SOL_THRESHOLD_USD):
        self.THRESHOLD_USD = SOL_THRESHOLD_USD
        self.SOL_PRICE = Decimal(str(get_price.CryptoPriceClient.get_price('SOL')))
        self.monitor = SolanaMonitor()

    async def get_block(self, slot, session):
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getBlock",
            "params": [
                slot,
                {
                    "transactionDetails": "full",
                    "rewards": False,
                    "maxSupportedTransactionVersion": 0
                }
            ]
        }
        try:
            async with session.post(SOL_RPC_URL, json=payload, timeout=10) as resp:
                return await resp.json()
        except Exception as e:
            logger.error(f"Error fetching slot {slot}: {e}")
            return None

    async def process_block(self, slot, session):
        while True:
            block = await self.get_block(slot, session)
            result = block.get("result") if block else None

            if result and "transactions" in result:
                for tx in result["transactions"]:
                    meta = tx.get("meta")
                    if not meta:
                        continue

                    pre = meta.get("preBalances", [])
                    post = meta.get("postBalances", [])
                    sig = tx["transaction"]["signatures"][0]
                    accounts = tx["transaction"]["message"]["accountKeys"]
                    
                    from_instr = to_instr = None
                    for inst in tx["transaction"]["message"].get("instructions", []):
                        parsed = inst.get("parsed")
                        if not parsed:
                            continue
                        if parsed.get("type") == "transfer":
                            info = parsed.get("info", {})
                            from_instr = info.get("source")
                            to_instr = info.get("destination")
                            break

                    for i, (b_pre, b_post) in enumerate(zip(pre, post)):
                        diff = b_post - b_pre
                        if diff == 0:
                            continue

                        sol_amount = Decimal(abs(diff)) / Decimal(LAMPORTS_PER_SOL)
                        usd_value = sol_amount * self.SOL_PRICE

                        if usd_value >= self.THRESHOLD_USD:
                            if from_instr and to_instr:
                                from_a = from_instr
                                to = to_instr
                            else:
                                if diff < 0:
                                    from_a = accounts[i]
                                    to = to_instr or "Unknown"
                                else:
                                    to = accounts[i]
                                    from_a = from_instr or "Unknown"

                            classification = "Unknown"

                            transaction = Transaction(
                                blockchain="SOL",
                                amount=float(sol_amount),
                                amount_usd=usd_value,
                                id=sig,
                                classification=classification,
                                link=f"https://solscan.io/tx/{sig}",
                                hash=sig,
                                from_a=from_a,
                                to=to,
                                value=float(sol_amount),
                                block_number=slot,
                                block_hash=None
                            )

                            logger.info(f"🐋 Whale Alert on SOL! {transaction}")
                            yield [transaction]

                return
            else:
                await asyncio.sleep(RETRY_DELAY)


    async def listen_whales(self):
        if self.SOL_PRICE == 0:
            logger.error("Failed to fetch SOL price. Aborting...")
            return
        # Debugging
        # logger.info("Fetching starting slot...")
        async with aiohttp.ClientSession() as session:
            payload = {"jsonrpc": "2.0", "id": 1, "method": "getSlot"}
            async with session.post(SOL_RPC_URL, json=payload) as resp:
                slot = (await resp.json())["result"]
            # Debugging
            # logger.info(f"Starting from slot: {slot}")
            while True:
                async for tx in self.process_block(slot, session, self.SOL_PRICE):
                    yield tx
                slot += 1
