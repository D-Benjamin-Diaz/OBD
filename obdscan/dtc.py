from __future__ import annotations

import obd
from rich.prompt import Confirm
from rich.table import Table

from .ui import console, header, pause

def _read(connection: obd.OBD, command: obd.OBDCommand, kind: str, table: Table) -> int:
    response = connection.query(command, force=True)
    codes = [] if response.is_null() else response.value
    
    for code, description in codes:
        table.add_row(code, kind, description or "Unknown")
    return len(codes)

def run(connection: obd.OBD) -> None:
    header("Check / erase codes")
    
    table = Table(border_style="cyan")
    table.add_column("Code", style="bold")
    table.add_column("Type")
    table.add_column("Description")
    
    with console.status("Reading codes . . ."):
        total = _read(connection, obd.commands.GET_DTC, "Stored", table)
        total += _read(connection, obd.commands.GET_CURRENT_DTC, "Pending", table)
    
    if total == 0:
        console.print("[green]No trouble codes found.[/]")
        pause()
        return
    
    console.print(table)
    console.print("\nClearing codes also erases the freeze frame and resets the car's emissions"
                    "readiness monitors.")
    if Confirm.ask("Erase all codes?", default=False):
        connection.query(obd.commands.CLEAR_DTC, force=True)
        console.print("[green]Clear command sent. Re-read to confirm.[/]")
    pause()