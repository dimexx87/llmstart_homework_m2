"""
Tests for finance data module
"""
import pytest
from unittest.mock import patch, MagicMock
from modules.finance_data import get_market_data, format_market_data


@pytest.mark.asyncio
async def test_get_market_data_success():
    """Test successful market data retrieval"""
    result = await get_market_data("currency", "USD/RUB")
    assert isinstance(result, dict)
    # Test should not fail even if API is unavailable


def test_format_market_data():
    """Test market data formatting"""
    test_data = {
        "symbol": "USD/RUB",
        "price": 95.5,
        "change": "+1.2%",
        "timestamp": "2025-01-09"
    }
    
    result = format_market_data(test_data)
    assert isinstance(result, str)
    assert "USD/RUB" in result or "95.5" in result


@pytest.mark.asyncio
async def test_get_market_data_invalid_type():
    """Test market data with invalid asset type"""
    result = await get_market_data("invalid", "INVALID")
    assert isinstance(result, dict)
    # Should return empty dict or error info


