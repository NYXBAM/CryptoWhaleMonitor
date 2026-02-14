import pytest
from unittest.mock import patch, MagicMock
from core.btc.parser import BitcoinWhaleParser
from models.dataclass import Transaction

@pytest.fixture
def parser():
    return BitcoinWhaleParser()

@pytest.fixture
def mock_whale_api_response():
    return [
        {
            "id": 8015189,
            "timestamp": 1771031267,
            "emoticons": "🚨🚨🚨🚨🚨",
            "amounts": [
                {
                    "symbol": "BTC",
                    "amount": 1651,
                    "value_usd": 113903569
                }
            ],
            "text": "transferred from unknown wallet to #Binance",
            "official": True,
            "link": "9c6f5f460bd8ba35554d7a00"
        },
        {
            "id": 8015020,
            "timestamp": 1771027715,
            "emoticons": "🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨",
            "amounts": [
                {
                    "symbol": "USDC",
                    "amount": 300000000,
                    "value_usd": 299981400
                }
            ],
            "text": "transferred from unknown wallet to unknown wallet",
            "official": True,
            "link": "60f2495c904db145ac4c7a00"
        }
    ]

@patch("core.btc.parser.requests.get")
def test_fetch_whale_alerts_parsing(mock_get, parser, mock_whale_api_response):
    
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = mock_whale_api_response
    mock_get.return_value = mock_resp

    results = parser.fetch_whale_alerts()

    assert len(results) == 2 
    
    btc_tx = results[0]
    assert isinstance(btc_tx, Transaction)
    assert btc_tx.blockchain == "BTC"
    assert btc_tx.amount == 1651
    assert btc_tx.amount_usd == 113903569
    assert btc_tx.id == 8015189
    assert "Binance" in btc_tx.classification
    assert btc_tx.link == "https://whale-alert.io/alert_click/9c6f5f460bd8ba35554d7a00"

    usdc_tx = results[1]
    assert usdc_tx.blockchain == "USDC"
    assert usdc_tx.amount == 300000000
    assert usdc_tx.amount_usd == 299981400
    
    

@patch("core.btc.parser.requests.get")
def test_fetch_whale_alerts_missing_fields(mock_get, parser):
    bad_data = [{
        "id": 999,
        "text": "Something happened",
        "link": "abc"
    }]
    mock_get.return_value.json.return_value = bad_data
    mock_get.return_value.status_code = 200

    results = parser.fetch_whale_alerts()
    assert results == []
    
@patch("core.btc.parser.requests.get")
def test_fetch_whale_alerts_invalid_amount(mock_get, parser):
    malformed_data = [{
        "id": 888,
        "amounts": [{"symbol": "BTC", "amount": None}],
        "text": "test",
        "link": "test"
    }]
    mock_get.return_value.json.return_value = malformed_data
    mock_get.return_value.status_code = 200

    results = parser.fetch_whale_alerts()
    assert len(results) == 0
    
@patch("core.btc.parser.requests.get")
def test_fetch_whale_alerts_timeout(mock_get, parser):
    import requests
    mock_get.side_effect = requests.exceptions.Timeout

    results = parser.fetch_whale_alerts()
    assert results == []
    

@patch("core.btc.parser.requests.get")
def test_fetch_whale_alerts_invalid_json(mock_get, parser):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.side_effect = ValueError("No JSON object could be decoded")
    mock_get.return_value = mock_resp

    results = parser.fetch_whale_alerts()
    assert results == []


@patch("core.btc.parser.requests.get")
def test_fetch_whale_alerts_http_error(mock_get, parser):
    import requests
    mock_resp = MagicMock()
    mock_resp.status_code = 403
    mock_resp.raise_for_status.side_effect = requests.exceptions.HTTPError("403 Forbidden")
    mock_get.return_value = mock_resp

    results = parser.fetch_whale_alerts()
    assert results == []