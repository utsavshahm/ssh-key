from rich.console import Console
from rich.theme import Theme

theme = Theme({
    "info":    "bold blue",
    "success": "bold green",
    "warn":    "bold yellow",
    "error":   "bold red",
    "accent":  "bold cyan",
    "muted":   "dim white",
})

console = Console(theme=theme)

def info(msg):    console.print(f"[info]→[/] {msg}")
def success(msg): console.print(f"[success]✓[/] {msg}")
def warn(msg):    console.print(f"[warn]![/] {msg}")
def error(msg):   console.print(f"[error]✗[/] {msg}"); raise SystemExit(1)
def header(msg):  console.print(f"\n[accent bold]{msg}[/]\n")
def divider():    console.print("[accent]" + "━" * 45 + "[/]")
def blank():      console.print()
