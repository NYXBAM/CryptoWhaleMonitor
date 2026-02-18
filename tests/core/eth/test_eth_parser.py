import pytest
from unittest.mock import patch, MagicMock
from core.eth.parser import EthParser
from models.dataclass import Transaction

@pytest.fixture
def parser():
    return EthParser(whale_threshold=100)

@patch("core.eth.parser.EthMonitor.get_block")
@patch("core.eth.parser.EthParser.check_tx")
def test_parse_block_filtering(mock_check, mock_get_block, parser):
    mock_get_block.return_value = {
        "hash": "0xblock_hash",
        "transactions": [
            {"hash": "0x1", "value": hex(10**18), "from": "0xA", "to": "0xB"},       # 1 ETH
            {"hash": "0x2", "value": hex(150*10**18), "from": "0xC", "to": "0xD"}   # 150 ETH
        ]
    }
    mock_check.return_value = "normal"

    whales = parser.parse_block(12345)

    assert len(whales) == 1
    
    tx = whales[0]
    assert isinstance(tx, Transaction)
    assert tx.blockchain == "ETH"     
    assert tx.amount == 150.0
    assert tx.hash == "0x2"
    assert tx.from_a == "0xC"
    assert tx.block_number == 12345
    assert "amount" in tx.to_dict()
    

@patch("core.eth.parser.requests.get")
def test_check_tx_deposit_to_exchange(mock_get, parser):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "from_address": "0xuser",
        "to_address": "0xexchange",
        "to_address_label": "Binance 3" 
    }
    mock_get.return_value = mock_resp

    with patch("core.eth.parser.KNOWN_EXCHANGES", ["Binance", "Kraken"]):
        result = parser.check_tx("0xhash")
        assert result == "deposit to: Binance 3"

@patch("core.eth.parser.requests.get")
def test_check_tx_normal(mock_get, parser):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        "from_address": "0x1",
        "to_address": "0x2",
        "from_address_label": None,
        "to_address_label": None
    }

    result = parser.check_tx("0xhash")
    assert result == "normal"
    
    
    
@patch("core.eth.parser.EthMonitor.get_block")
def test_parse_block_contract_creation(mock_get_block, parser):
    """
    Test handling of contract creation transactions where 'to' is None.
    """
    mock_get_block.return_value = {
        "hash": "0xblock_hash",
        "transactions": [
            {
                "hash": "0xcontract_deploy",
                "value": hex(200 * 10**18), # 200 ETH
                "from": "0xcreator",
                "to": None # IMPORTANT: 'to' is None in contract creation
            }
        ]
    }

    with patch.object(parser, 'check_tx', return_value="normal"):
        whales = parser.parse_block(12345)

    assert len(whales) == 1
    assert whales[0].to is None  
    assert whales[0].amount == 200.0
    
@patch("core.eth.parser.requests.get")
def test_check_tx_api_error_handling(mock_get, parser):
    """Test check_tx returns None when API fails (status 500)"""
    mock_resp = MagicMock()
    mock_resp.status_code = 500
    mock_get.return_value = mock_resp

    result = parser.check_tx("0xsomehash")
    
    assert result is None