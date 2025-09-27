#!/usr/bin/env -S uv run

"""
Yasashii Anki - Command Line Entry Point
Japanese Dictionary Lookup Tool for Creating Anki Cards
"""

import argparse
from rich.console import Console
from rich.progress import track

# Import our custom modules
from .logging import logger
from .japanese_word import JapaneseWord
from .anki_client import AnkiClient

# Set up Rich console
console = Console()

parser = argparse.ArgumentParser(
        description='🌸 Yasashii Anki - Japanese Dictionary Lookup Tool for Creating Anki Cards! 🌸',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  yasashii 力               # Look up a single word
  yasashii 誰も 犬          # Look up multiple words
  yasashii -f words.txt     # Process words from file
  yasashii 行く --create    # Look up word and create Anki card
  yasashii 食べる 寝る --create  # Look up multiple words and create Anki cards
        """
    )
parser.add_argument('words', 
                    nargs='*',
                    help='🔍 Japanese words to look up (can specify multiple)')
parser.add_argument('-f', '--file', 
                    type=str,
                    help='📁 Path to a text file containing Japanese words (one per line)')
parser.add_argument('-c', '--create',
                    action='store_true',
                    help='🗂️ Create card(s) in Anki')
args = parser.parse_args()

def process_single_word(word_text, create=False):
    """Process and display a single Japanese word"""
    try:
        logger.info(f"Looking up word: {word_text}", "🔍")
        
        word = JapaneseWord(word_text)
        
        if word.meaning:
            word.display()
            if create:
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
        else:
            logger.warning(f"No translation found for: {word_text}", "❓")
            logger.info("Try checking the spelling or using a different form of the word", "💡")
    

    except Exception as e:
        logger.error(f"Error processing word '{word_text}': {e}")


def process_words_from_file(file_path, create=False):
    """Read words from a text file and display their meanings"""
    try:
        logger.info(f"Reading words from file: {file_path}", "📖")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            words = [line.strip() for line in f if line.strip()]
        
        logger.success(f"Found {len(words)} words to process", "🎯")
        logger.header(f"Processing Words from {file_path}", "📂")
        
        # Process words with progress bar
        processed_words = []
        for word_text in track(words, description="🔍 Looking up words..."):
            if word_text:  # Skip empty lines
                word = JapaneseWord(word_text)
                processed_words.append(word)
        
        if create:
            client = AnkiClient()
        # Display results after progress is complete
        console.print()  # Add spacing after progress bar
        for word in processed_words:
            word.display()
            console.print()  # Add spacing between words
            if create:
                try:
                    logger.info(f"Creating Anki card for: {word.word}", "📝")
                    client.create_card(word.meaning)
                    logger.success(f"Successfully created Anki card for: {word.word}", "🎴")
                except Exception as e:
                    if "duplicate" in str(e).lower():
                        logger.warning(f"Card for '{word.word}' already exists in deck", "🔄")
                    else:
                        logger.error(f"Failed to create card for '{word.word}': {e}", "❌")
        
        logger.success(f"Completed processing {len(words)} words!", "🎉")
                
    except FileNotFoundError:
        logger.error(f"File '{file_path}' not found.")
    except Exception as e:
        logger.error(f"Error processing file: {e}")

def process_multiple_words(words, create=False):
    """Process multiple Japanese words"""
    logger.success(f"{len(words)} words to process", "🎯")
    
    # Process words with progress bar
    processed_words = []
    for word_text in track(words, description="🔍 Looking up words..."):
        if word_text:  # Skip empty strings
            word = JapaneseWord(word_text)
            processed_words.append(word)
    
    if create:
        client = AnkiClient()
    
    # Display results after progress is complete
    console.print()  # Add spacing after progress bar
    for word in processed_words:
        word.display()
        console.print()  # Add spacing between words
        if create:
            try:
                logger.info(f"Creating Anki card for: {word.word}", "📝")
                client.create_card(word.meaning)
                logger.success(f"Successfully created Anki card for: {word.word}", "🎴")
            except Exception as e:
                if "duplicate" in str(e).lower():
                    logger.warning(f"Card for '{word.word}' already exists in deck", "🔄")
                else:
                    logger.error(f"Failed to create card for '{word.word}': {e}", "❌")
    
    logger.success(f"Completed processing {len(words)} words!", "🎉")


def main():
    """Main function with argument parsing"""

    console.rule("🌸 Yasashii Anki 🌸", style="magenta")

    try:
        if args.file:
            # Process words from file
            process_words_from_file(args.file, create=args.create)
        elif args.words:
            # Process words from command line arguments
            if len(args.words) == 1:
                process_single_word(args.words[0], create=args.create)
            else:
                process_multiple_words(args.words, create=args.create)
        else:
            logger.info("No arguments provided, showing help", "🌸")
            parser.print_help()
        
        logger.success("Thanks for using Yasashii! 頑張って!", "🎌")
        
    except KeyboardInterrupt:
        logger.warning("Operation cancelled by user", "⏹️")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", "💥")


if __name__ == "__main__":
    main()
