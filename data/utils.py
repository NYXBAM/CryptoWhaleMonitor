# data/utils.py
from sqlalchemy import text
from utils.send_telegram_channel import send_telegram_message
from .db import SessionLocal
from .models import WhaleTransaction
import json
import os
import logging

logger = logging.getLogger("CryptoWhaleMonitor")

def get_explorer_url(blockchain):
    if blockchain == 'BTC':
        return "https://blockchain.com/explorer/transactions/btc/"
    if blockchain == 'ETH':
        return "https://etherscan.io/tx/"
    if blockchain == 'TON':
        return "https://tonscan.org/tx/"
    elif blockchain == 'XRP':
        return "https://xrpscan.com/tx/"
    
def get_classification_label(classification):
    classification = classification or "Unknown / normal transfer"
    if classification.startswith("withdrawal"):
        exchange = classification.split("withdrawal from: ")[-1]
        return f"➡️ 🏦 Withdrawal from: {exchange}"
    elif classification.startswith("deposit"):
        exchange = classification.split("deposit to: ")[-1]
        return f"⬅️ 🏦 Deposit to: {exchange}"
    
    elif classification.startswith("exchange"):
        return "🔄 🏦 Exchange-to-exchange transfer"
    
    elif classification.startswith("From:") or classification.startswith("To:"):
        return classification
    
    else:
        return "🔄 Unknown|normal transfer"

def db_add(blockchain, amount, classification):
    """for whale-io alerts"""
    db = SessionLocal()
    whale_tx = WhaleTransaction(
        blockchain=blockchain,
        amount=amount,
        classification=classification,
        block_hash_or_number="not_available", 
        txid=None,
        from_address=None,
        to_address=None
    )
    
    db.add(whale_tx)
    try:
        db.commit()
        logger.info(f"Added to DB: {blockchain} {amount} {classification}")
    except Exception as e:
        db.rollback()
        logger.error(f"Error adding to DB: {e}")
    finally:
        db.close()
    
    
def save_whale_txs(blockchain: str, whales: list):
    """
    Save whale transactions to the database and send Telegram alerts.
    :param blockchain: 'BTC' or 'ETH'
    :param whales: List of whale transaction dicts
    """ 
    db = SessionLocal()
    try:
        for tx in whales:
            txid = tx.hash or tx.block_hash  or tx.id # TODO 
            amount = tx.amount or tx.value
            
            exists = db.query(WhaleTransaction).filter_by(txid=txid).first()
            if exists:
                return False
            send_telegram_message(
                f"🐳 <b>${blockchain} Whale Alert!</b>\n\n"
                f"💰 Amount: <b>{tx.amount:.2f} {blockchain}</b>\n"
                f"🟢 From: <b>{tx.from_a[:6]}…{tx.from_a[-4:]}</b>\n"
                f"🔴 To: <b>{tx.to[:6]}…{tx.to[-4:]}</b>\n"
                f"🏦 Classification: {get_classification_label(tx.classification)}\n"
                f"🔗 Tx: <a href='{get_explorer_url(blockchain)}{tx.hash}'>{tx.hash[:12]}…</a>\n"
                f"🌐 Explorer: <a href='{get_explorer_url(blockchain)}{tx.hash}'>View Transaction</a>"
                )
            logging.info(f"${blockchain} Whale Alert:\n{amount} {blockchain}, Tx {txid}, from {tx.from_a} → {tx.to}\nSended to Telegram channel")

            whale = WhaleTransaction(
                blockchain=blockchain,
                txid=txid,
                from_address=tx.from_a or 'Unknown', 
                to_address=tx.to or 'Unknown',       
                amount=amount,
                block_hash_or_number=tx.block_hash or 'Unknown',
                classification=tx.classification or None        
            )
            db.add(whale)
        db.commit()
    except Exception as e:
        db.rollback()
        logging.error(f"Error saving whales: {e}")
    finally:
        db.close()
    return True

def load_seen_hashes(filename='alerts_hashes.json'):
    if os.path.exists(filename):
        try:
            with open(filename, 'r') as f:
                return set(json.load(f))
        except (json.JSONDecodeError, FileNotFoundError):
            return set()
    return set()

def save_seen_hashes(hashes, filename='alerts_hashes.json'):
    with open(filename, 'w') as f:
        json.dump(list(hashes), f)

def add_price_column(engine):
    try:
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE whale_transactions ADD COLUMN price REAL"))
            conn.commit()
    except Exception as e:
        error_msg = str(e)
        if "duplicate column name" in error_msg or "already exists" in error_msg:
            pass
        else:
            logger.error(f"Error with add price column {e}")
            raise e
        
