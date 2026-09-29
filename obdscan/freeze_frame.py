from __future__ import annotations

import obd
from rich.table import Table
from .ui import console, format_value, header, pause
from .connection import Session

def run(session: Session) -> None:
    header('Freeze Frame')
    table =  Table(border_style="cyan")
    table.add_column("Parameter")
    table.add_column("Value", justify="right")
    
    with console.status("Reading freeze frame . . ."):
        for cmd in session.freeze:
            response = session.connection.query(cmd, force=True)
            table.add_row(str(cmd.desc or cmd.name), format_value(response))
    
    if session.freeze:
        console.print(table)
    else:
        console.print("[yellow]This car returned no freeze frame data during discovery.[/]")
    
    pause()