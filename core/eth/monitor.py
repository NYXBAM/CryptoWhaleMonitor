from config import ETH_RPC_URL
import requests



class EthMonitor:
    '''Class to monitor Ethereum blockchain using JSON-RPC'''
    def __init__(self, url=ETH_RPC_URL):
        self.ETH_RPC_URL = url
        
    def rpc_call(self, method, params=[]):
        payload = {"jsonrpc":"2.0","method":method,"params":params,"id":1}
        r = requests.post(self.ETH_RPC_URL, json=payload)
        r.raise_for_status()
        result_json = r.json()
        if "error" in result_json:
            raise Exception(result_json["error"])
        return result_json["result"]

    def get_latest_block_number(self):
        block_hex = self.rpc_call("eth_blockNumber")
        return int(block_hex, 16)

    def get_block(self, block_number):
        return self.rpc_call("eth_getBlockByNumber", [hex(block_number), True])

    @staticmethod
    def wei_to_eth(wei):
        return int(wei, 16) / 1e18
