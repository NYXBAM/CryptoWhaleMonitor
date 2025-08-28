from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from .db import Base

class WhaleTransaction(Base):
    __tablename__ = "whale_transactions"

    id = Column(Integer, primary_key=True, index=True)
    blockchain = Column(String, nullable=False)
    txid = Column(String, unique=True, index=True)
    from_address = Column(String)
    to_address = Column(String)
    amount = Column(Float, nullable=False)
    block_hash_or_number = Column(String, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
