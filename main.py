import json
import argparse
from rich.console import Console
from rich.panel import Panel
from rich.progress import track

# Import our custom modules
from auto_anki_maker.logging import logger
from auto_anki_maker.japanese_word import JapaneseWord, jp_words
from auto_anki_maker.anki_client import AnkiClient

# Set up Rich console
console = Console()


def process_single_word(word_text, create=False):
    """Process and display a single Japanese word"""
    try:
        logger.info(f"Looking up word: {word_text}", "🔍")
        logger.header(f"Word Lookup", "📚")
        
        word = JapaneseWord(word_text)
        
        if word.meaning:
            word.display()
            logger.success(f"Found translation for: {word_text}", "✨")
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

def main():
    """Main function with argument parsing"""
    # Welcome message
    console.rule("🌸 Auto-Anki Maker 🌸", style="magenta")
    logger.info("Starting Japanese Dictionary Lookup Tool", "🚀")
    
    parser = argparse.ArgumentParser(
        description='🌸 Japanese Dictionary Lookup Tool - Create beautiful Anki cards! 🌸',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py -w 力             # Look up a single word
  python main.py --word 食べる     # Same as above
  python main.py -f words.txt      # Process words from file
  python main.py --demo            # Run interactive demo
        """
    )
    parser.add_argument('-f', '--file', 
                        type=str,
                        help='📁 Path to a text file containing Japanese words (one per line)')
    parser.add_argument('-w', '--word',
                        type=str,
                        help='🔍 Look up a single Japanese word')
    parser.add_argument('-d', '--demo',
                        action='store_true',
                        help='🌸 Run a demo')
    parser.add_argument('-c', '--create',
                        action='store_true',
                        help='🗂️ Create card(s) in Anki')
    args = parser.parse_args()
    
    try:
        if args.file:
            # Process words from file
            process_words_from_file(args.file, create=args.create)
        elif args.word:
            # Process single word
            process_single_word(args.word, create=args.create)
        else:
            logger.info("No arguments provided, doing nothing", "🌸")
            logger.info("Try: uv run main.py --help for usage options", "💡")
        
        logger.success("Thanks for using Auto-Anki Maker! 頑張って!", "🎌")
        
    except KeyboardInterrupt:
        logger.warning("Operation cancelled by user", "⏹️")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", "💥")


if __name__ == "__main__":
    main()
