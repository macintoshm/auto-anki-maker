#!/usr/bin/env python3
"""Example usage of the AnkiClient class"""

from auto_anki_maker.anki_client import AnkiClient
from auto_anki_maker.logging import logger

def main():
    """Demonstrate AnkiClient usage"""
    logger.header("Anki Connect API Example", "🎴")
    
    # Create AnkiClient instance
    client = AnkiClient()
    logger.info(f"Connected to Anki at: {client.api_url}", "🔗")
    logger.info(f"Target deck: {client.deck_name}", "📚")
    
    try:
        # Get cards from the default deck (from .env)
        logger.info("Fetching cards from default deck...", "🔍")
        cards = client.get_cards()
        logger.success(f"Found {len(cards)} cards in deck '{client.deck_name}'", "✨")
        
        if cards:
            logger.info("First few card IDs:", "📋")
            for i, card_id in enumerate(cards[:5], 1):
                logger.info(f"  {i}. Card ID: {card_id}", "🎴")
            
            if len(cards) > 5:
                logger.info(f"  ... and {len(cards) - 5} more cards", "📚")
        else:
            logger.warning("No cards found in the deck", "❓")
            
    except Exception as e:
        logger.error(f"Failed to get cards: {e}", "💥")
        logger.info("Make sure Anki is running and AnkiConnect addon is installed", "💡")
        logger.info("AnkiConnect addon: https://ankiweb.net/shared/info/2055492159", "🔗")

if __name__ == "__main__":
    main()
