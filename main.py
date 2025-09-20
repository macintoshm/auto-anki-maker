import json
import jmespath
import argparse
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.progress import track
from rich import print as rprint
import logging

# Set up Rich console
console = Console()

# Set up colorful logging
class ColorfulLogger:
    """Custom logger with rich colors and emojis"""
    
    def __init__(self):
        self.console = Console()
    
    def info(self, message, emoji="ℹ️"):
        self.console.print(f"{emoji} [blue]{message}[/blue]")
    
    def success(self, message, emoji="✅"):
        self.console.print(f"{emoji} [green]{message}[/green]")
    
    def warning(self, message, emoji="⚠️"):
        self.console.print(f"{emoji} [yellow]{message}[/yellow]")
    
    def error(self, message, emoji="❌"):
        self.console.print(f"{emoji} [red]{message}[/red]")
    
    def header(self, title, emoji="🌸"):
        panel = Panel(
            Text(title, style="bold magenta"), 
            border_style="magenta",
            title=f"{emoji} Auto-Anki Maker {emoji}"
        )
        self.console.print(panel)
    
    def word_result(self, word_data, emoji="📚"):
        """Display a single word result beautifully"""
        if not word_data:
            return
            
        table = Table(show_header=False, border_style="cyan", padding=(0, 1), width=80)
        table.add_column("Field", style="bold cyan", no_wrap=True, width=12)
        table.add_column("Value", style="white", max_width=65)
        
        table.add_row("Word", f"[bold yellow]{word_data.get('word', 'N/A')}[/bold yellow]")
        table.add_row("Reading", f"[green]{', '.join(word_data.get('readings', []))}[/green]")
        table.add_row("Meaning", f"[blue]{', '.join(word_data.get('meanings', [])[:3])}[/blue]")
        table.add_row("Type", f"[magenta]{', '.join(word_data.get('part_of_speech', []))}[/magenta]")
        
        if word_data.get('examples'):
            example = word_data['examples'][0]
            table.add_row("Example", f"[dim white]{example['sentences']['japanese']}[/dim white]")
            table.add_row("Translation", f"[dim cyan]{example['sentences']['english']}[/dim cyan]")
        
        self.console.print(Panel(
            table, 
            title=f"{emoji} {word_data.get('word', 'Word')}", 
            border_style="cyan",
            width=84
        ))

# Create global logger instance
logger = ColorfulLogger()

with open('jmdict-with-examples.json', 'r') as f:
    jmdict_words = json.load(f).get('words')

class JapaneseWord(str):
    """Extended string class for Japanese words with dictionary lookup capabilities"""
    
    def _get_jp_word(self, word: str, prefer_common=True, max_senses=3):
        """
        Get Japanese word with options to filter results
        
        Args:
            word: The word to search for
            prefer_common: If True, prioritize common readings/kanji
            max_senses: Maximum number of senses to return per word
        """
        # 1. Search in kanji.text
        expr_kanji = jmespath.compile(f"[?kanji[?text=='{word}']]")
        result = expr_kanji.search(jmdict_words)
        if result:
            return self._filter_and_rank_results(result, prefer_common, max_senses)

        # 2. If not found, search in kana.text
        expr_kana = jmespath.compile(f"[?kana[?text=='{word}']]")
        result = expr_kana.search(jmdict_words)
        if result:
            return self._filter_and_rank_results(result, prefer_common, max_senses)

        # 3. Nothing found
        return None

    def _filter_and_rank_results(self, results, prefer_common=True, max_senses=3):
        """Filter and rank results to get the best matches"""
        if not results:
            return None
            
        # Sort results by preference
        if prefer_common:
            # Prioritize entries with common kanji/kana
            results.sort(key=lambda x: (
                # First sort by whether it has common kanji
                -any(k.get('common', False) for k in x.get('kanji', [])),
                # Then by whether it has common kana
                -any(k.get('common', False) for k in x.get('kana', [])),
                # Finally by ID (earlier entries are often more common)
                int(x.get('id', '999999'))
            ))
        
        # Take the best result and limit senses
        best_result = results[0].copy()
        if max_senses and len(best_result.get('sense', [])) > max_senses:
            best_result['sense'] = best_result['sense'][:max_senses]
            
        return best_result
    
    def get_primary_meaning(self, max_examples=2):
        """Get the primary meaning of this Japanese word"""
        word = super().__str__()
        result = self._get_jp_word(word, prefer_common=True, max_senses=1)
        if result and result.get('sense'):
            primary_sense = result['sense'][0]
            
            # Extract example sentences
            examples = []
            for example in primary_sense.get('examples', [])[:max_examples]:
                example_entry = {
                    'japanese_text': example.get('text', ''),
                    'sentences': []
                }
                
                for sentence in example.get('sentences', []):
                    if sentence.get('land') == 'jpn':
                        japanese_sentence = sentence.get('text', '')
                    elif sentence.get('land') == 'eng':
                        english_sentence = sentence.get('text', '')
                
                # Find matching Japanese and English pairs
                jpn_sentences = [s.get('text', '') for s in example.get('sentences', []) if s.get('land') == 'jpn']
                eng_sentences = [s.get('text', '') for s in example.get('sentences', []) if s.get('land') == 'eng']
                
                if jpn_sentences and eng_sentences:
                    example_entry['sentences'] = {
                        'japanese': jpn_sentences[0],
                        'english': eng_sentences[0]
                    }
                    examples.append(example_entry)
            
            return {
                'word': word,
                'readings': [k['text'] for k in result.get('kana', []) if k.get('common', False)][:2],
                'kanji': [k['text'] for k in result.get('kanji', []) if k.get('common', False)][:2],
                'meanings': [g['text'] for g in primary_sense.get('gloss', [])],
                'part_of_speech': primary_sense.get('partOfSpeech', []),
                'examples': examples
            }
        return None
    
    def format_display(self):
        """Display the word using colorful logging"""
        meaning = self.get_primary_meaning()
        if not meaning:
            logger.warning(f"No translation found for: {super().__str__()}", "❓")
            return ""
        
        logger.word_result(meaning)
        return ""  # Return empty string since logging handles display
    
    def display(self):
        """Display the word using colorful logging (for explicit display calls)"""
        self.format_display()
    
    def __str__(self):
        """Return the formatted display when printed"""
        self.format_display()
        return f"JapaneseWord('{super().__str__()}')"  # Return simple representation
    
    def __repr__(self):
        """Return representation for debugging"""
        return f"JapaneseWord('{super().__str__()}')"
    
    @staticmethod
    def format_multiple_words(words_list):
        """Format and display multiple words in a nice readable format"""
        logger.header("Processing Multiple Words", "📚")
        
        # Process words with progress bar
        processed_words = []
        for word_str in track(words_list, description="🔍 Looking up words..."):
            word = JapaneseWord(word_str)
            processed_words.append(word)
        
        # Display results after progress is complete
        console.print()  # Add spacing after progress bar
        for word in processed_words:
            word.display()
            console.print()  # Add spacing between words


def jp_words(word_list):
    """Convert a list of strings to JapaneseWord objects"""
    return [JapaneseWord(word) for word in word_list]

def process_single_word(word_text):
    """Process and display a single Japanese word"""
    try:
        logger.info(f"Looking up word: {word_text}", "🔍")
        logger.header(f"Word Lookup", "📚")
        
        word = JapaneseWord(word_text)
        meaning = word.get_primary_meaning()
        
        if meaning:
            word.display()
            logger.success(f"Found translation for: {word_text}", "✨")
        else:
            logger.warning(f"No translation found for: {word_text}", "❓")
            logger.info("Try checking the spelling or using a different form of the word", "💡")
                
    except Exception as e:
        logger.error(f"Error processing word '{word_text}': {e}")

def process_words_from_file(file_path):
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
        
        # Display results after progress is complete
        console.print()  # Add spacing after progress bar
        for word in processed_words:
            word.display()
            console.print()  # Add spacing between words
        
        logger.success(f"Completed processing {len(words)} words!", "🎉")
                
    except FileNotFoundError:
        logger.error(f"File '{file_path}' not found.")
    except Exception as e:
        logger.error(f"Error processing file: {e}")

def run_demo():
    """Run the demo showing different usage patterns"""
    logger.header("Auto-Anki Maker Demo", "🌸")
    
    # Method 1: Individual word processing
    logger.info("Method 1: Individual Word Processing", "🎯")
    words = ['行く', '来る', '食べる']
    for word_str in words:
        word = JapaneseWord(word_str)
        word.display()
        console.print()
    
    # Method 2: Batch processing
    logger.info("Method 2: Batch Processing", "📦")
    jp_word_list = jp_words(['行く', '来る', '食べる'])
    for word in jp_word_list:
        word.display()
        console.print()
    
    # Method 3: JSON output
    logger.info("Method 3: Raw JSON Data", "📋")
    word = JapaneseWord('行く')
    result = word.get_primary_meaning()
    
    # Create a beautiful JSON display
    json_panel = Panel(
        json.dumps(result, indent=2, ensure_ascii=False),
        title="📄 JSON Data Structure",
        border_style="green"
    )
    console.print(json_panel)

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
    args = parser.parse_args()
    
    try:
        if args.file:
            # Process words from file
            process_words_from_file(args.file)
        elif args.word:
            # Process single word
            process_single_word(args.word)
        elif args.demo:
            # Run the demo
            run_demo()
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
