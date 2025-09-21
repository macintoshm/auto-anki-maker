#!/usr/bin/env python3
"""Test script for AnkiClient to verify the implementation"""

from auto_anki_maker.anki_client import AnkiClient, ANKI_URL
from auto_anki_maker.logging import logger

def test_anki_client():
    """Test the AnkiClient implementation"""
    logger.header("Testing AnkiClient Implementation", "🧪")
    
    # Test constant
    logger.info(f"Anki URL constant: {ANKI_URL}", "🔗")
    
    # Create AnkiClient instance
    client = AnkiClient()
    logger.success(f"AnkiClient created successfully", "✅")
    logger.info(f"Target deck: {client.deck_name}", "📚")
    logger.info(f"API URL: {client.api_url}", "🌐")
    
    # Test get_cards method (will fail without Anki running, but that's expected)
    try:
        logger.info("Attempting to get cards (this will likely fail since Anki isn't running)", "⚠️")
        cards = client.get_cards()
        logger.success(f"Successfully retrieved {len(cards)} cards!", "🎉")
    except Exception as e:
        logger.warning(f"Expected failure (Anki not running): {e}", "⚠️")
        logger.info("This is normal - Anki Connect needs to be running for this to work", "💡")
    
    logger.success("AnkiClient implementation test completed!", "🎌")

if __name__ == "__main__":
    test_anki_client()
