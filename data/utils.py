# data/utils.py
from utils.send_telegram_channel import send_telegram_message
from .db import SessionLocal
from .models import WhaleTransaction


def get_explorer_url(blockchain):
    if blockchain == 'BTC':
        # return "https://btcscan.org/tx/"
        return "https://blockchain.com/explorer/transactions/btc/"
    elif blockchain == 'ETH':
        return "https://etherscan.io/tx/"
    
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
    else:
        return "🔄 Unknown|normal transfer"

    
def save_whale_txs(blockchain: str, whales: list):
    """
    Save whale transactions to the database and send Telegram alerts.
    :param blockchain: 'BTC' or 'ETH'
    :param whales: List of whale transaction dicts
    """
    db = SessionLocal()
    try:
        for tx in whales:
            txid = tx.get('txid') or tx.get('hash') 
            amount = tx.get('amount') or tx.get('value')
            
            exists = db.query(WhaleTransaction).filter_by(txid=txid).first()
            if exists:
                continue 
            send_telegram_message(
                f"🐳 <b>${blockchain} Whale Alert!</b>\n\n"
                f"💰 Amount: <b>{amount:.2f} {blockchain}</b>\n"
                f"🟢 From: <b>{tx.get('from','Unknown')[:6]}…{tx.get('from','Unknown')[-4:]}</b>\n"
                f"🔴 To: <b>{tx.get('to','Unknown')[:6]}…{tx.get('to','Unknown')[-4:]}</b>\n"
                f"🏦 Classification: {get_classification_label(tx.get('classification','Unknown'))}\n"
                f"🔗 Tx: <a href='{get_explorer_url(blockchain)}{txid}'>{txid[:12]}…</a>\n"
                f"🌐 Explorer: <a href='{get_explorer_url(blockchain)}{txid}'>View Transaction</a>"
            )


            whale = WhaleTransaction(
                blockchain=blockchain,
                txid=txid,
                from_address=tx.get('from', 'Unknown'),
                to_address=tx.get('to', 'Unknown'),
                amount=amount,
                block_hash_or_number=tx.get('block_hash', tx.get('block_number', 'Unknown')),
                classification=tx.get('classification', None)
            )
            db.add(whale)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error saving whales: {e}")
    finally:
        db.close()
