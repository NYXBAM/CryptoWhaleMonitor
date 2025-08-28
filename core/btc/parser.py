from .monitor import BitcoinMonitor
from config import BTC_WHALE_THRESHOLD, KNOWN_EXCHANGES
import requests


class BitcoinParser(BitcoinMonitor):
    '''Class to parse Bitcoin blocks and identify whale transactions'''
    def __init__(self):
        super().__init__()
        self.whale_threshold = BTC_WHALE_THRESHOLD

    def check_address(self, address: str) -> str:
        """Check BTC address label via WalletExplorer API."""
        url = f"https://www.walletexplorer.com/api/1/address-lookup?address={address}"
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code != 200:
                print(f"❌ Error {resp.status_code} for address {address}")
                return None

            data = resp.json()
            print(data)
            wallet_info = data.get("wallet")
            if wallet_info and wallet_info.get("label"):
                
                return wallet_info["label"]
            return None
        except Exception as e:
            print(f"❌ Exception checking address {address}: {e}")
            return None

    def parse_block(self, block_hash):
        txs = self.get_btc_block_txs(block_hash)
        whales = []

        for tx in txs:
            total_satoshi = sum(v['value'] for v in tx['vout'])
            total_btc = self.satoshi_to_btc(total_satoshi)
            if total_btc >= self.whale_threshold:
                from_addr = "Unknown"
                if tx.get('vin') and len(tx['vin']) > 0:
                    vin0 = tx['vin'][0]
                    if vin0 and vin0.get('prevout'):
                        from_addr = vin0['prevout'].get('scriptpubkey_address', 'Unknown')
                    elif vin0.get('is_coinbase', False):
                        from_addr = "Coinbase"

                to_addr = "Unknown"
                if tx.get('vout') and len(tx['vout']) > 0:
                    to_addr = tx['vout'][0].get('scriptpubkey_address', 'Unknown')

                from_lbl = self.check_address(from_addr)
                to_lbl = self.check_address(to_addr)
                print(from_lbl, to_lbl)

                classification = "normal"  # default

                if from_lbl:
                    for exch in KNOWN_EXCHANGES:
                        if exch in from_lbl:
                            classification = f"withdrawal from: {from_lbl}"
                            break

                if to_lbl and classification == "normal": 
                    for exch in KNOWN_EXCHANGES:
                        if exch in to_lbl:
                            classification = f"deposit to: {to_lbl}"
                            break

                whales.append({
                    "txid": tx['txid'],
                    "block_hash": block_hash,
                    "amount": total_btc,
                    "from": from_addr,
                    "to": to_addr,
                    "classification": classification
                })

        return whales
