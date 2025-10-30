"""
Test Telegram bot functions
"""

import pytest
from traffic_share.bot.bot import get_bot
from traffic_share.bot.utils.message_templates import (
    welcome_message, balance_message, stats_message
)


def test_get_bot():
    """Test bot instance creation"""
    bot = get_bot()
    assert bot is not None


def test_welcome_message():
    """Test welcome message template"""
    message = welcome_message("TestUser")
    assert "TestUser" in message
    assert "Traffic Share" in message


def test_balance_message():
    """Test balance message template"""
    message = balance_message(10.50, 100.00)
    assert "10.50" in message
    assert "100.00" in message


def test_stats_message():
    """Test stats message template"""
    message = stats_message(
        daily_gb=5.0, daily_usd=2.50,
        weekly_gb=30.0, weekly_usd=15.00,
        total_gb=100.0, total_usd=50.00
    )
    assert "5.00" in message
    assert "2.50" in message


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
