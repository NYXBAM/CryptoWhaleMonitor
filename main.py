### by NYXBAM ### 
# TG CHANNEL:  https://t.me/CryptoTransac

import uvicorn
from api.v1.app import app
from core.btc.monitor import *
from core.eth.monitor import * 
from core.btc.parser import *
from core.eth.parser import *
from core.ton.monitor import TonMonitor
from core.xrp.parser import XRPParser



from data.analytics.ai_report import generate_and_send
from data.db import engine, Base
from data.models import WhaleTransaction
from data.utils import *

from models.dataclass import Transaction
from utils.send_telegram_channel import send_telegram_message
from config import API, ETH_WHALE_THRESHOLD

import time
import hashlib
import json
import asyncio
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/logging.log", encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)


logger = logging.getLogger("CryptoWhaleMonitor")


Base.metadata.create_all(bind=engine)
# adding column for exist db 
add_price_column(engine=engine)

        
async def btc_parser():
    while True:
        try:
            # Debug 
            logger.info("Starting $BTC PARSER")
            btc_whale = BitcoinWhaleParser()
            seen_hashes = load_seen_hashes()
            alerts = []
            new_alerts = btc_whale.fetch_whale_alerts()
            fresh_alerts = []
            for a in new_alerts:
                alert_str = json.dumps(a.to_dict(), sort_keys=True)  
                alert_hash = hashlib.sha256(alert_str.encode()).hexdigest()
                if alert_hash not in seen_hashes:
                    seen_hashes.add(alert_hash)
                    fresh_alerts.append(a)
                
                if fresh_alerts:
                    save_seen_hashes(seen_hashes)
            if fresh_alerts:
                for a in fresh_alerts:
                    # Debug
                    logger.info(f"${a.blockchain} whale: {a.amount} {a.classification}")
                    db_add(a.blockchain, a.amount, a.classification)

                alerts.extend(fresh_alerts)

                for a in fresh_alerts:
                    message = (
                        f"🐳 <b>${a.blockchain} Whale-Alert.io!</b>\n\n"
                        f"💰 Amount: <b>{a.amount:.2f} {a.blockchain}</b>\n"
                        f"💵 USD Value: ${a.amount_usd:,.2f}\n"
                        f"🏦 Classification: {a.classification}\n"
                        f"🔗 Link: <a href='{a.link}'>View Alert</a>"
                    )
                    send_telegram_message(message)

        except Exception as e:
            logger.error(f"$BTC PARSING ERROR: {e}")
        await asyncio.sleep(90)
    
async def eth_parser():
    while True:
        logger.info("Starting $ETH PARSER")
        eth_parser = EthParser(whale_threshold=ETH_WHALE_THRESHOLD)
        last_eth_block = None
        try:
            latest_eth_block = eth_parser.get_latest_block_number()
            if latest_eth_block != last_eth_block:
                whales = eth_parser.parse_block(latest_eth_block)
                for tx in whales:
                    #dbg
                    # logging.info(f"🚨 $ETH whale: {tx.value:.2f} ETH, Tx {tx.hash} , from {tx.from_a} → {tx.to}")
                    save_whale_txs("ETH", whales)
                last_eth_block = latest_eth_block
        except Exception as e:
            logger.error(f"$ETH ERROR: {e}")
        await asyncio.sleep(60)

async def xrp_parser():
    logger.info("Starting $XRP PARSER")
    while True:
        try:
            async for whales in XRPParser.listen_whales():
                for tx in whales:
                    if save_whale_txs("XRP", [tx]):
                        logger.info(f"$XRP Transaction {tx.hash} processed")
                    else:
                        logger.info(f"$XRP Transaction {tx.hash} already exists in DB")
        except Exception as e:
            logger.error(f"$XRP PARSER ERROR: {e}")

async def ton_parser():
    logger.info("Starting $TON PARSER")
    monitor = TonMonitor()
    await monitor.start_monitoring()
    
async def analytics():
    logger.info("Starting analytics...")
    while True:
        try:
            await asyncio.to_thread(generate_and_send)
            logger.info("Report generated and send in telegram")
        except Exception as e:
            logger.error(f"Error {e} in sending analytics")
        await asyncio.sleep(2 * 60 * 60)

async def main():
    tasks = []
    if API == True:
        api_task = asyncio.create_task(
            uvicorn.Server(
                uvicorn.Config(app, host="0.0.0.0", port=8080, log_level="info")
            ).serve()
        )
        tasks.append(api_task)
    
    parser_tasks = [
        asyncio.create_task(ton_parser()),
        asyncio.create_task(xrp_parser()),
        asyncio.create_task(eth_parser()),
        asyncio.create_task(btc_parser()),
        asyncio.create_task(analytics()),
    ]
    
    tasks.extend(parser_tasks)
    await asyncio.gather(*tasks)



if __name__ == "__main__":
    asyncio.run(main())
