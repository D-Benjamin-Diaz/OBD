from __future__ import annotations

from rich.prompt import Prompt

from . import dtc, freeze_frame, live, logger
from .connection import connect, discover
from .ui import console, header
import sys

from . import demo

MENU = {
    "1" : ("Check / erase codes", lambda s: dtc.run(s.connection)),
    "2" : ("Display freeze frame", freeze_frame.run),
    "3" : ("Live data table", live.run),
    "4" : ("Drive data collection (CSV)", logger.run)
}

def main() -> None:
    header("Connecting")
    connection = demo.connect() if "--demo" in sys.argv else connect()
    if connection is None:
        return
    
    session = discover(connection)
    console.input("\n[dim]Press Enter to continue...[/]")
    
    try:
        while True:
            header("Main menu")
            for key, (label, _) in MENU.items():
                console.print(f"  [bold cyan]{key}[/] {label}")
            console.print("  [bold cyan]q[/] Quit\n")
            
            choice = Prompt.ask("Select", choices=[*MENU, "q"])
            
            if choice == "q":
                break
            MENU[choice][1](session)
    finally:
        connection.close()
        
if __name__ == "__main__":
    main()