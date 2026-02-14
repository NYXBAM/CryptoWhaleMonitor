from dataclasses import asdict, dataclass
from typing import Optional

@dataclass(slots=True)
class Transaction():
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
    
    def __post_init__(self):
        if self.amount is None:
            raise ValueError("Amount cannot be None")
        if not self.blockchain:
            raise ValueError("Blockchain symbol is required")
        
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    
    
