"""Anki Connect API client for interfacing with Anki desktop application"""

import os
import json
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Anki Connect API URL
ANKI_URL = '127.0.0.1:8765'

class AnkiClient:
    """Client for connecting to the Anki Connect API"""
    
    def __init__(self):
        self.api_url = f"http://{ANKI_URL}"
        self.deck_name = os.getenv('AUTO_ANKI_DECK_NAME')
    
    def post(self, payload):
        try:
            # Make POST request to Anki Connect API
            response = requests.post(self.api_url, json=payload, timeout=10)
            response.raise_for_status()  # Raise exception for HTTP errors
            
            # Parse JSON response
            data = response.json()
            
            # Check if API returned an error
            if data.get('error') is not None:
                raise ValueError(f"Anki API error: {data['error']}")
            
            # Return the list of card IDs
            return data.get('result', [])
        except requests.exceptions.RequestException as e:
            raise requests.RequestException(f"Failed to connect to Anki Connect API at {self.api_url}: {e}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response from Anki Connect API: {e}")
        except Exception as e:
            raise Exception(f"Unexpected error while getting cards: {e}")


    def get_cards(self, deck=None):
        """
        Get cards from a specific deck
        
        Args:
            deck (str, optional): Name of the deck. If not provided, uses ANKI_DECK_NAME from .env
            
        Returns:
            list: List of card IDs from the deck
            
        Raises:
            requests.RequestException: If the API request fails
            ValueError: If the API returns an error
        """
        # Use provided deck name or fall back to environment variable
        target_deck = deck if deck is not None else self.deck_name
        
        # Prepare the API request payload
        payload = {
            "action": "findCards",
            "params": {"query": f"deck:{target_deck}"},
            "version": 6
        }
        return self.post(payload)

    def get_card_info(self, card_ids):
        """
        Get card information from a specific deck
        
        Args:
            card_ids (list): List of card IDs
            
        Returns:
            list: List of card information
        """
        if not isinstance(card_ids, list):
            card_ids = [card_ids]

        payload = {
                "action": "cardsInfo",
                "version": 6,
                "params": {
                    "cards": card_ids
                }
        }
        
        return self.post(payload)

    def create_card(self, card_info):
        """
        Create a new card in the Anki deck
        
        Args:
            card_info (dict): Dictionary containing card information
        """
        card_type=os.getenv('AUTO_ANKI_CARD_TYPE')
        word_field=os.getenv('AUTO_ANKI_WORD_FIELD')
        reading_field=os.getenv('AUTO_ANKI_READING_FIELD')
        meaning_field=os.getenv('AUTO_ANKI_MEANING_FIELD')
        part_of_speech_field=os.getenv('AUTO_ANKI_PART_OF_SPEECH_FIELD')
        sentence_field=os.getenv('AUTO_ANKI_SENTENCE_FIELD')
        sentence_translation_field=os.getenv('AUTO_ANKI_SENTENCE_TRANSLATION_FIELD')
        audio_field=os.getenv('AUTO_ANKI_AUDIO_FIELD')
        

        payload = {
            "action": "addNote",
            "version": 6,
            "params": {
                "note": {
                    "deckName": self.deck_name,
                    "modelName": card_type,
                    "fields": {
                        word_field: card_info.get('word'),
                        reading_field: card_info.get('readings'),
                        meaning_field: card_info.get('meanings'),
                        part_of_speech_field: card_info.get('part_of_speech'),
                        sentence_field: card_info.get('sentences'),
                        sentence_translation_field: card_info.get('sentence_translations')
                    },
                    "tags": [
                        "auto-anki"
                    ],
                    "audio": {
                        "url": "https://assets.languagepod101.com/dictionary/japanese/audiomp3.php?kanji=猫&kana=ねこ",
                        "filename": "yomichan_ねこ_猫.mp3",
                        "skipHash": "7e2c2f954ef6051373ba916f000168dc",
                    "fields": [
                        audio_field
                    ]
                    }
                }
            }
        }
        
        return self.post(payload)
