import pytest
import requests
from unittest.mock import patch, MagicMock
from core.btc.monitor import BitcoinMonitor

@pytest.fixture
def monitor():
    return BitcoinMonitor(api_url="https://fake-api.com")

def test_satoshi_to_btc(monitor):
    assert monitor.satoshi_to_btc(100_000_000) == 1.0
    assert monitor.satoshi_to_btc(50_000_000) == 0.5
    assert monitor.satoshi_to_btc(1) == 0.00000001
    assert monitor.satoshi_to_btc(0) == 0

@patch("core.btc.monitor.requests.get")
def test_get_btc_latest_block_hash(mock_get, monitor):
    mock_get.return_value.text = "000000000000000000032f5"
    result = monitor.get_btc_latest_block_hash()
    
    assert result == "000000000000000000032f5"
    mock_get.assert_called_once_with("https://fake-api.com/blocks/tip/hash", timeout=30)

@patch("core.btc.monitor.requests.get")
def test_get_btc_block_txs(mock_get, monitor):
    mock_data = [
        {"txid": "tx1", "value": 1000},
        {"txid": "tx2", "value": 2000}
    ]
    mock_get.return_value.json.return_value = mock_data
    
    result = monitor.get_btc_block_txs("fake_hash")
    
    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0]["txid"] == "tx1"
    mock_get.assert_called_once_with("https://fake-api.com/block/fake_hash/txs", timeout=30)
    

@patch("core.btc.monitor.requests.get")
def test_get_btc_latest_block_hash_error(mock_get, monitor):
    mock_resp = MagicMock()
    mock_resp.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Client Error")
    mock_get.return_value = mock_resp

    result = monitor.get_btc_latest_block_hash()
    
    assert result is None 

@patch("core.btc.monitor.requests.get")
def test_get_btc_block_txs_timeout(mock_get, monitor):
    mock_get.side_effect = requests.exceptions.Timeout("Connection timed out")

    result = monitor.get_btc_block_txs("fake_hash")
    
    assert result == [] 