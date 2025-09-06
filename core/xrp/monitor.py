import requests
from typing import Optional, Dict
from config import XRP_SCAN_API

import logging

logger = logging.getLogger("CryptoWhaleMonitor")


class XRPMonitor:
    """Monitor XRP transactions and classify them using xrpscan API."""
    def __init__(self):
        self.xrpscan_api = XRP_SCAN_API
    
    def get_address_classification(self, tx_hash: str) -> Optional[Dict]:
        try:
            response = requests.get(f"{self.xrpscan_api}{tx_hash}")
            response.raise_for_status()
            data = response.json()
            account_name = data.get('AccountName') or {}
            destination_name = data.get('DestinationName') or {}
        
            address_info = {
            'from_name': account_name.get('name'),
            'from_domain': account_name.get('domain'),
            'to_name': destination_name.get('name'), 
            'to_domain': destination_name.get('domain')
        }
            
            classification_parts = []
            if address_info['from_name']:
                classification_parts.append(f"From: {address_info['from_name']}")
            if address_info['from_domain']:
                classification_parts.append(f"({address_info['from_domain']})")
            if address_info['to_name']:
                classification_parts.append(f"To: {address_info['to_name']}")
            if address_info['to_domain']:
                classification_parts.append(f"({address_info['to_domain']})")
                
            return ' '.join(classification_parts) if classification_parts else None
            
        except Exception as e:
            logger.error(f"Error fetching address info from xrpscan: {e}")
            return None
        
        


