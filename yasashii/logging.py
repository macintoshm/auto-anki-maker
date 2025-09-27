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
            
        self.console.print(f"\n{emoji} [bold cyan]{word_data.get('word', 'Word')}[/bold cyan]")
        self.console.print(f"[bold cyan]Word:\t\t[/bold cyan][bold yellow]{word_data.get('word', 'N/A')}[/bold yellow]")
        self.console.print(f"[bold cyan]Reading:\t[/bold cyan][green]{', '.join(word_data.get('readings', []))}[/green]")
        self.console.print(f"[bold cyan]Meaning:\t[/bold cyan][blue]{word_data.get('meanings', '')}[/blue]")
        self.console.print(f"[bold cyan]Type:\t\t[/bold cyan][magenta]{', '.join(word_data.get('part_of_speech', []))}[/magenta]")
        
        if word_data.get('examples'):
            example = word_data['examples'][0]
            self.console.print(f"[bold cyan]Example:\t[/bold cyan][dim white]{example['sentences']['japanese']}[/dim white]")
            self.console.print(f"[bold cyan]Translation:\t[/bold cyan][dim cyan]{example['sentences']['english']}[/dim cyan]")
        
        self.console.print()


# Create global logger instance
logger = ColorfulLogger()
