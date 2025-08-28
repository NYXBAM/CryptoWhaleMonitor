from .monitor import BitcoinMonitor
from config import BTC_WHALE_THRESHOLD



class BitcoinParser(BitcoinMonitor):
    '''Class to parse Bitcoin blocks and identify whale transactions'''
    def __init__(self):
        super().__init__()
        self.whale_threshold = BTC_WHALE_THRESHOLD

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

                whales.append({
                    "txid": tx['txid'],
                    "block_hash": block_hash,
                    "amount": total_btc,
                    "from": from_addr,
                    "to": to_addr
                })

        return whales
