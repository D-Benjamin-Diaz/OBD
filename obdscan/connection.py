from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Any, Dict
import obd
from serial.tools import list_ports
from rich.progress import BarColumn, Progress, TextColumn, TimeRemainingColumn
from rich.table import Table

from .ui import console, is_empty

LIVE_MODE, FREEXE_MODE, MONITOR_MODE = 1, 2, 6

SKIP_PREFIXES = ("PIDS_", "MIDS_")

@dataclass
class Session:
    """Connection plus the commands this car actually answers."""
    connection: obd.OBD
    live: List[obd.OBDCommand] = field(default_factory=list)
    freeze: List[obd.OBDCommand] = field(default_factory=list)
    monitors: List[obd.OBDCommand] = field(default_factory=list)

def _pick_port() -> Optional[str]:
    ports = list(list_ports.comports())
    if not ports:
        return None
    if len(ports) == 1:
        return ports[0].device
    
    console.print("[bold]Available ports:[/]")
    
    for i, p in enumerate(ports, 1):
        console.print(f"    {i}. {p.device}  [dim]{p.description}[/]")
    
    choice = console.input("Select port number: ").strip()
    if choice.isdigit() and 1 <= int(choice) <= len(ports):
        return ports[int(choice) - 1].device
    
    return None

def connect() -> Optional[obd.OBD]:
    '''Open the connection. Returns None if the car cannot be reached'''
    port = _pick_port()
    
    if port is None:
        console.print("[red]No serial port found. Check the cable and its drier[/]")
        return None
    
    with console.status(f"Connecting on {port}"):
        connection = obd.OBD(portstr=port)
    
    status = connection.status()
    if status == obd.OBDStatus.CAR_CONNECTED:
        console.print(f"[green]Connected[/] via {connection.port_name()}" 
                        f"({connection.protocol_nme()})")
        return connection
    
    if status == obd.OBDStatus.ELM_CONNECTED:
        console.print("[red]Adapter found but the car does not answer. "
                        "Turn the ignition on.[/]")
    else:
        console.print("[red]Could not open the adapter.[/]")
    connection.close()
    return None

def _candidates(mode: int) -> List[obd.OBDCommand]:
    try:
        commands = obd.commands[mode]
    except IndexError:
        return []
    return [c for c in commands if c and not c.name.startswith(SKIP_PREFIXES)]

def _is_plain(value: Any) -> bool:
    """True for numbers, text, and short tuples of them (loggable to CSV)."""
    simple = (int, float, str, bool)
    
    if hasattr(value, "magnitude") or isinstance(value, simple):
        return True
    if isinstance(value, (tuple, list)):
        return all(v is None or isinstance(v, simple) for v in value)
    
    return False

def discover(connection: obd.OBD) -> Session:
    """Probe every known command once and keep only those that answer."""
    session = Session(connection)
    groups = [
        (LIVE_MODE, "Live Data", session.live),
        (FREEXE_MODE, "Freeze frame", session.freeze),
        (MONITOR_MODE, "Mode 6 tests", session.monitors)
    ]
    
    progress = Progress(
        TextColumn("{task.description:<14}"), BarColumn(),
        TextColumn("{task.completed}/{task.total}"), TimeRemainingColumn(),
        console=console
    )
    with progress:
        for mode, label, bucket in groups:
            commands = _candidates(mode)
            task = progress.add_task(label, total=len(commands))
            for command in commands:
                try:
                    response = connection.query(command, force=True)
                except Exception:
                    response = None
                progress.advance(task)
                if is_empty(response):
                    continue
                
                if mode == LIVE_MODE and not _is_plain(response.value):
                    continue
                
                bucket.append(command)
    
    table = Table(title="Discovered on this car", border_style = "cyan")
    table.add_column("Group")
    table.add_column("Commands", justify="right")
    for _, label, bucket in groups:
        table.add_row(label, str(len(bucket)))
    console.print(table)
    
    if not (session.live or session.freeze or session.monitors):
        console.print("[yellow]Nothing answered. Is the ignition on?[/]")
    return session

def _plain(value: Any) -> Any:
    return round(value.magnitude, 3) if hasattr(value, "magnitude") else value

def read_monitors(session: Session) -> List[Dict[str, Any]]:
    """One row per mode 6 test: value, limits and pass/fail."""
    rows: List[Dict[str, Any]] = []
    
    for command in session.monitors:
        response = session.connection.query(command, force=True)
        if is_empty(response):
            continue
        
        tests = getattr(response.value, "tests", None) or {}
        
        for tid, test in tests.items():
            rows.append({
                "monitor": command.name,
                "test": getattr(test, "desc", None) or getattr(test, "name", None) or f"TID {tid}",
                "value": _plain(getattr(test, "value", None)),
                "min": _plain(getattr(test, "min", None)),
                "max": _plain(getattr(test, "max", None)),
                "passed": _plain(getattr(test, "passed", None))
            })
            
    return rows



