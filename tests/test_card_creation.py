#!/usr/bin/env python3
"""Test the enhanced card creation with logging"""

from auto_anki_maker.japanese_word import JapaneseWord
from auto_anki_maker.anki_client import AnkiClient
from auto_anki_maker.logging import logger

def test_card_creation():
    """Test card creation with logging"""
    logger.header("Testing Card Creation with Enhanced Logging", "🧪")
    
    # Test with a word that exists
    word_text = "行く"
    word = JapaneseWord(word_text)
    
    if word.meaning:
        word.display()
        logger.success(f"Found translation for: {word_text}", "✨")
        
        # Test the card creation with logging
        client = AnkiClient()
        try:
            logger.info(f"Creating Anki card for: {word_text}", "📝")
            client.create_card(word.meaning)
            logger.success(f"Successfully created Anki card for: {word_text}", "🎴")
        except Exception as e:
            if "duplicate" in str(e).lower():
                logger.warning(f"Card for '{word_text}' already exists in deck", "🔄")
            else:
                logger.error(f"Failed to create card for '{word_text}': {e}", "❌")

if __name__ == "__main__":
    test_card_creation()
