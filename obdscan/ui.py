from __future__ import annotations

from typing import Any, Optional
from rich.console import Console
from rich.panel import Panel

console = Console()

def header(title: str) -> None:
    console.clear()
    console.print(Panel.fit(f"[bold cyan]OBD Scanner[/] | {title}", border_style="cyan"))
    console.print()

def pause() -> None:
    console.input("\n[dim]Press Enter to return to the menu[/]")
    

def is_empty(response: Any) -> bool:
    return response is None or  response.is_null()

def format_value(response: Any) -> str:
    if is_empty(response):
        return "n/a"
    val = response.value
    if hasattr(val, "magnitude"):
        return f"{val.magnitude:.1f} {val.units:~P}"
    return str(val)

def numeric_value(response: Any) -> Optional[Any]:
    '''Raw number for CSV export, or NONE if there is no data'''
    if is_empty(response):
        return None
    value = response.value
    return round(value.magnitude, 3) if hasattr(value, "magnitude") else value

def unit_of(response: Any) -> str:
    if is_empty(response):
        return ""
    
    return f"{response.value.units:~P}"