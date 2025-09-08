from dataclasses import dataclass
from typing import Optional

@dataclass(slots=True)
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

'''  # if u have error, just remove slots=True, this feat work only python 3.10+, for older version. uncomment code below 
from typing import Optional

class Transaction:
    __slots__ = ['blockchain', 'amount', 'amount_usd', 'id', 'classification', 
                 'link', 'hash', 'from_a', 'to', 'value', 'block_number', 'block_hash']
    
    def __init__(self, 
                 blockchain: Optional[str] = None,
                 amount: Optional[float] = None,
                 amount_usd: Optional[float] = None,
                 id: Optional[str] = None,
                 classification: Optional[str] = None,
                 link: Optional[str] = None,
                 hash: Optional[str] = None,
                 from_a: Optional[str] = None,
                 to: Optional[str] = None,
                 value: Optional[float] = None,
                 block_number: Optional[int] = None,
                 block_hash: Optional[str] = None):
        self.blockchain = blockchain
        self.amount = amount
        self.amount_usd = amount_usd
        self.id = id
        self.classification = classification
        self.link = link
        self.hash = hash
        self.from_a = from_a
        self.to = to
        self.value = value
        self.block_number = block_number
        self.block_hash = block_hash
'''

    
    
