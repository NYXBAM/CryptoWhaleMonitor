from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict
from config import DATABASE_URL
from data.models import WhaleTransaction



class WhaleTransactionRepository:
    def __init__(self, database_url: str = DATABASE_URL):
        self.engine = create_engine(database_url, echo=False)
        self.Session = sessionmaker(bind=self.engine)

    def get_last_n_transactions(self, n: int = 50) -> List[Dict]:
        with self.Session() as db:
            query = db.query(WhaleTransaction).order_by(desc(WhaleTransaction.timestamp))
            transactions = query.limit(n).all()
            return [self._to_dict(tx) for tx in transactions]

    def get_transactions_since(self, hours: int = 1) -> List[Dict]:
        with self.Session() as db:
            time_threshold = datetime.now(timezone.utc) - timedelta(hours=hours)
            query = db.query(WhaleTransaction).filter(WhaleTransaction.timestamp >= time_threshold)
            transactions = query.order_by(desc(WhaleTransaction.timestamp)).all()
            return [self._to_dict(tx) for tx in transactions]

    def get_transaction_by_txid(self, txid: str) -> Optional[Dict]:
        with self.Session() as db:
            tx = db.query(WhaleTransaction).filter_by(txid=txid).first()
            return self._to_dict(tx) if tx else None

    def _to_dict(self, tx: WhaleTransaction) -> Dict:
        return {
            "blockchain": tx.blockchain,
            "txid": tx.txid,
            "from_address": tx.from_address,
            "to_address": tx.to_address,
            "amount": tx.amount,
            "price": tx.price,
            "classification": tx.classification,
            "timestamp": tx.timestamp.isoformat(),
        }