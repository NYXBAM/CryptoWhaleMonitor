import pytest
from unittest.mock import patch, MagicMock
from core.eth.monitor import EthMonitor
from requests.exceptions import HTTPError, Timeout

@pytest.fixture
def eth_monitor():
    return EthMonitor(url="https://fake-eth-rpc.com")

def test_wei_to_eth(eth_monitor):
    # 1 ETH in HEX = 0xde0b6b3a7640000
    wei_hex = "0xde0b6b3a7640000"
    assert eth_monitor.wei_to_eth(wei_hex) == 1.0
    # very small amount: 0.0001 ETH = 100000000000000 WEI
    assert eth_monitor.wei_to_eth(hex(10**18)) == 1.0
    
@patch("core.eth.monitor.requests.post")
def test_wei_to_eth_edge_cases(mock_post, eth_monitor):
    """Test boundary values for Wei to ETH conversion"""
    # Zero Wei
    assert eth_monitor.wei_to_eth("0x0") == 0.0
    
    # Very large number (e.g., total supply or whale movement)
    # 100,000,000 ETH in hex
    large_hex = hex(10**8 * 10**18)
    assert eth_monitor.wei_to_eth(large_hex) == 100000000.0

@patch("core.eth.monitor.requests.post")
def test_get_latest_block_number(mock_post, eth_monitor):
    mock_post.return_value.json.return_value = {
        "jsonrpc": "2.0",
        "id": 1,
        "result": "0x1121d7c" # 17964412 in decimal
    }
    mock_post.return_value.status_code = 200

    result = eth_monitor.get_latest_block_number()

    assert result == 17964412
    assert isinstance(result, int)
    args, kwargs = mock_post.call_args
    assert kwargs['json']['method'] == "eth_blockNumber"

@patch("core.eth.monitor.requests.post")
def test_get_block_empty_transactions(mock_post, eth_monitor):
    """Test case where a block exists but has no transactions (edge case for empty blocks)"""
    mock_post.return_value.json.return_value = {
        "jsonrpc": "2.0",
        "result": {
            "number": "0x5",
            "transactions": []
        }
    }
    
    result = eth_monitor.get_block(5)
    assert result["transactions"] == []
    assert len(result["transactions"]) == 0

@patch("core.eth.monitor.requests.post")
def test_rpc_call_http_error(mock_post, eth_monitor):
    """Test handling of HTTP status errors (e.g., 404, 500) using raise_for_status"""
    # Setup mock to raise HTTPError when raise_for_status() is called
    mock_post.return_value.raise_for_status.side_effect = HTTPError("500 Server Error")
    
    with pytest.raises(HTTPError) as excinfo:
        eth_monitor.rpc_call("eth_blockNumber")
    assert "500 Server Error" in str(excinfo.value)


@patch("core.eth.monitor.requests.post")
def test_rpc_call_timeout(mock_post, eth_monitor):
    """Test handling of network timeouts during RPC call"""
    mock_post.side_effect = Timeout("Request timed out")
    
    with pytest.raises(Timeout):
        eth_monitor.rpc_call("eth_blockNumber")
    
@patch("core.eth.monitor.requests.post")
def test_get_block_not_found(mock_post, eth_monitor):
    """Test behavior when a block number is requested that doesn't exist yet (returns None)"""
    mock_post.return_value.json.return_value = {
        "jsonrpc": "2.0",
        "result": None
    }
    
    # In Ethereum RPC, requesting a non-existent block returns null (None in Python)
    result = eth_monitor.get_block(999999999)
    assert result is None
  
@patch("core.eth.monitor.requests.post")
def test_rpc_call_malformed_json(mock_post, eth_monitor):
    """Test handling of invalid JSON response from the RPC node"""
    mock_post.return_value.json.side_effect = ValueError("No JSON object could be decoded")
    
    with pytest.raises(ValueError):
        eth_monitor.rpc_call("eth_blockNumber") 
        
@patch("core.eth.monitor.requests.post")
def test_rpc_call_error_from_node(mock_post, eth_monitor):
    mock_post.return_value.json.return_value = {
        "jsonrpc": "2.0",
        "id": 1,
        "error": {"code": -32000, "message": "Too many requests"}
    }
    
    with pytest.raises(Exception) as excinfo:
        eth_monitor.rpc_call("any_method")
    
    assert "Too many requests" in str(excinfo.value)

@patch("core.eth.monitor.requests.post")
def test_get_block_with_transactions(mock_post, eth_monitor):
    mock_block_data = {
        "number": "0x1",
        "transactions": [{"hash": "0xabc", "value": "0xde0b6b3a7640000"}]
    }
    mock_post.return_value.json.return_value = {
        "jsonrpc": "2.0",
        "result": mock_block_data
    }

    result = eth_monitor.get_block(1)

    assert result["number"] == "0x1"
    assert len(result["transactions"]) == 1
    args, kwargs = mock_post.call_args
    assert kwargs['json']['params'][0] == "0x1"