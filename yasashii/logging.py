"""Colorful logging module with Rich library support and emojis"""

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table

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
            title=f"{emoji} Yasashii Anki {emoji}"
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
