from dataclasses import dataclass
from typing import Optional

@dataclass
class Transaction:
    "dataclass represented a blockchain transaction"
    blockchain: Optional[str] = None
    amount: Optional[float] = None 
    amount_usd: Optional[float] = None
    id: Optional[str] = None
    classification: Optional[str] = None
    link: Optional[str] = None
    hash: Optional[str] = None
    from_a: Optional[str] = None
    to: Optional[str] = None
    value: Optional[float] = None
    block_number: Optional[int] = None
    block_hash: Optional[str] = None
    
    
    def to_dict(self) -> dict:
        return {
            'blockchain': self.blockchain,
            'amount': self.amount,
            'amount_usd': self.amount_usd,
            'id': self.id,
            'classification': self.classification,
            'link': self.link,
            'hash': self.hash,
            'from_a': self.from_a,
            'to': self.to,
            'value': self.value,
            'block_number': self.block_number,
            'block_hash': self.block_hash
        }
    
    
    
