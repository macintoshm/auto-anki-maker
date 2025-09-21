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
        self.deck_name = os.getenv('ANKI_DECK_NAME', '日本語')
    
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
