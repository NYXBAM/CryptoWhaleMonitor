from .monitor import BitcoinMonitor
from config import BTC_WHALE_THRESHOLD, KNOWN_EXCHANGES
import requests
import time
from typing import List, Dict


class BitcoinParser(BitcoinMonitor):
    '''Class to parse Bitcoin blocks and identify whale transactions'''
    def __init__(self):
        super().__init__()
        self.whale_threshold = BTC_WHALE_THRESHOLD

    def check_address(self, address: str) -> bool:
        """Check if BTC address is likely an exchange wallet using Mempool.space API."""
        if not address or address == 'Unknown':
            return False
        
        url = f'https://mempool.space/api/address/{address}'
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code != 200:
                print(f"❌ Error {resp.status_code} for address {address}")
                return False

            data = resp.json()
            tx_count = data['chain_stats']['tx_count']
            funded_sum = data['chain_stats']['funded_txo_sum']  
            
            # Exchange wallet: >100 transactions or >10 BTC received
            is_exchange = tx_count > 100 or funded_sum > 1_000_000_000  # 10 BTC
            print(f"Address {address}: tx_count={tx_count}, funded_sum={funded_sum/100_000_000} BTC, "
                  f"Exchange: {is_exchange}")
            time.sleep(0.2)  # Small delay to avoid overwhelming API
            return is_exchange

        except Exception as e:
            print(f"❌ Exception checking address {address}: {e}")
            return False

    def parse_transaction(self, txid: str) -> Dict:
        """Parse a single transaction and classify it as exchange-related or normal."""
        url = f'https://mempool.space/api/tx/{txid}'
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code != 200:
                print(f"❌ Error {resp.status_code} for txid {txid}")
                return None

            tx = resp.json()
            total_satoshi = sum(vout['value'] for vout in tx['vout'])
            total_btc = self.satoshi_to_btc(total_satoshi)

            # Skip if not a whale transaction
            if total_btc < self.whale_threshold:
                print(f"Transaction {txid}: {total_btc} BTC is below whale threshold ({self.whale_threshold} BTC)")
                return None

            # Get from/to addresses
            from_addr = "Unknown"
            if tx.get('vin') and len(tx['vin']) > 0:
                vin0 = tx['vin'][0]
                if vin0.get('prevout'):
                    from_addr = vin0['prevout'].get('scriptpubkey_address', 'Unknown')
                elif vin0.get('is_coinbase', False):
                    from_addr = "Coinbase"

            to_addr = "Unknown"
            if tx.get('vout') and len(tx['vout']) > 0:
                to_addr = tx['vout'][0].get('scriptpubkey_address', 'Unknown')

            is_from_exchange = self.check_address(from_addr)
            is_to_exchange = self.check_address(to_addr)

            classification = "normal transaction"
            if is_from_exchange and is_to_exchange:
                classification = "exchange-to-exchange transfer"
            elif is_from_exchange:
                classification = "withdrawal from exchange"
            elif is_to_exchange:
                classification = "deposit to exchange"

            result = {
                "txid": tx['txid'],
                "block_hash": tx.get('status', {}).get('block_hash', 'Unknown'),
                "amount": total_btc,
                "from": from_addr,
                "to": to_addr,
                "classification": classification
            }
            print(f"Classified {txid} as: {classification}")
            return result

        except Exception as e:
            print(f"❌ Exception parsing transaction {txid}: {e}")
            return None

    def parse_block(self, block_hash: str) -> List[Dict]:
        """Parse a block and return whale transactions."""
        txs = self.get_btc_block_txs(block_hash)
        whales = []

        for tx in txs:
            result = self.parse_transaction(tx['txid'])
            if result:
                whales.append(result)

        return whales