"""Auto-Anki Maker - Japanese Dictionary Lookup Tool for Anki Card Creation"""

from .logging import ColorfulLogger, logger
from .japanese_word import JapaneseWord, jp_words
from .anki_client import AnkiClient

__version__ = "1.0.0"
__author__ = "Auto-Anki Maker"

__all__ = ["ColorfulLogger", "logger", "JapaneseWord", "jp_words", "AnkiClient"]
