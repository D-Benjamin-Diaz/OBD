from __future__ import annotations
from .connection import Session

import obd
from rich.live import Live
from rich.table import Table

from .ui import console, format_value, header

def _build_table(rows) -> Table:
    table = Table(title="Live data (Ctrl + C to stop)", border_style="cyan")
    table.add_column("Parameter")
    table.add_column("Value", justify="right", style="bold")
    for name, value in rows:
        table.add_row(name, value)
    return table

def run(session: Session) -> None:
    header("Live Data")
    connection, commands = session.connection, session.live
    
    if not commands:
        console.print("[yellow]No supported live parameters found[/]")
        console.input("\nPress Enter to return ...")
        return
    
    with Live(console=console, refresh_per_second=4) as live:
        try:
            while True:
                rows = [(str(c.desc or c.name), format_value(connection.query(c))) for c in commands]
                live.update(_build_table(rows))
        except KeyboardInterrupt:
            pass
        