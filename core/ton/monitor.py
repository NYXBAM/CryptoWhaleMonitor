
import logging
from config import TON_WHALE_THRESHOLD
from core.ton.parser import TonParser
import time

from data.utils import save_whale_txs

logger = logging.getLogger("CryptoWhaleMonitor")

class TonMonitor(TonParser):
    def __init__(self, sleep_interval=1):
        super().__init__()
        self.sleep_interval = sleep_interval

    def start_monitoring(self):
        logger.info("Starting TON whale monitor...")
        while True:
            try:
                new_txs = self.fetch_new_txs(self.latest_lt)
                whales = self.process_whales(new_txs)
                logger.debug(whales)

                for tx in whales:
                    if tx.amount >= TON_WHALE_THRESHOLD: 
                        save_whale_txs("TON", [tx])
                        logger.info(
                            f"{tx.classification} Whale TX {tx.hash}: {tx.from_a} -> {tx.to} : {tx.amount:.2f} TON - link: {tx.link}"
                        )
            except Exception as e:
                logger.error(f"Error: {e}")
            time.sleep(self.sleep_interval)
