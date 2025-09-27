"""Japanese word lookup and processing module"""

import json
import jmespath
import os
from rich.progress import track
from rich.console import Console
from .logging import logger
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up Rich console
console = Console()

# Load the Japanese dictionary data
dict_path = os.getenv('JMDICT_PATH')
with open(dict_path, 'r') as f:
    jmdict_words = json.load(f).get('words')

class JapaneseWord(str):
    """Extended string class for Japanese words with dictionary lookup capabilities"""

    def __init__(self, word: str):
        super().__init__()
        self.word = word
        self.meaning = self._get_primary_meaning()
    
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
    
    def _get_primary_meaning(self, max_examples=2):
        """Get the primary meaning of this Japanese word"""
        result = self._get_jp_word(self.word, prefer_common=True, max_senses=1)
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

            meanings = [g['text'] for g in primary_sense.get('gloss', [])]
            
            # Format meanings as numbered list
            formatted_meanings = '\n'.join([f"{i+1}. {meaning}" for i, meaning in enumerate(meanings)])
            
            return {
                'word': self.word,
                'readings': [k['text'] for k in result.get('kana', []) if k.get('common', False)][:2],
                'kanji': [k['text'] for k in result.get('kanji', []) if k.get('common', False)][:2],
                'meanings': formatted_meanings,
                'part_of_speech': primary_sense.get('partOfSpeech', []),
                'examples': examples
            }
        return None
    

    def display(self):
        """Display the word using colorful logging (for explicit display calls)"""
        if not self.meaning:
            logger.warning(f"No translation found for: {self.word}", "❓")
        else:
            logger.word_result(self.meaning)

    def __str__(self):
        """Return a formatted string representation of the word"""
        if not self.meaning:
            return f"JapaneseWord('{self.word}') - No translation found"
            
        readings = ', '.join(self.meaning.get('readings', []))
        meanings = self.meaning.get('meanings', '')  # Already formatted as numbered list
        if readings:
            return f"{self.word} ({readings}) - {meanings}"
        else:
            return f"{self.word} - {meanings}"
    
    def __repr__(self):
        """Return detailed representation for debugging"""
        if not self.meaning:
            return f"JapaneseWord('{self.word}', found=False)"
            
        readings = self.meaning.get('readings', [])
        meanings = self.meaning.get('meanings', [])
        examples = self.meaning.get('examples', [])
        
        return (f"JapaneseWord('{self.word}', found=True, "
                f"readings={len(readings)}, meanings={len(meanings)}, "
                f"examples={len(examples)})")
    
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
