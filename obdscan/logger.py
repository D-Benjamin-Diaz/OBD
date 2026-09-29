from __future__ import annotations

import csv
import time
from datetime import datetime
from pathlib import Path

import obd
from rich.live import Live
from rich.panel import Panel
from rich.prompt import Confirm

from .connection import Session, read_monitors
from .ui import console, header, pause, unit_of, numeric_value

LOG_DIR = Path("logs")

def _status_panel(path: Path, samples: int, elapsed: float) -> Panel:
    text = (f"[bold]Recording[/] to {path}\n"
            f"Samples: {samples} \n"
            f"Elapsed: {elapsed: 0.0f} s\n\n"
            f"[dim]Press Ctrl + C to stop and save.[/]")
    return Panel(text, title="Drive Data Collection", border_style="green")


def run(session: Session)-> None:
    header("Drive data collection")
    connection, commands = session.connection, session.live
    
    if not commands:
        console.print("[yellow]No supported live parameters found.[/]")
        pause()
        return
    
    LOG_DIR.mkdir(exist_ok=True)
    path = LOG_DIR / f"drive_{datetime.now():%Y%m%d_%H%M%S}.csv"
    
    console.print(f"Loging {len(commands)} parameters to [bold]{path}[/]")
    
    if not Confirm.ask('Start Recording?', default=True):
        return
    
    responses = [connection.query(c) for c in commands]
    columns = ["timestam", "elapsed_s"] + [
        f"{c.name} ({unit_of(r)})" if unit_of(r) else c.name
        for c, r in zip(commands, responses)
    ]
    
    samples = 0
    start = time.perf_counter()
    with path.open("w", newline="", encoding="utf-8") as f, \
            Live(console=console, refresh_per_second=4) as live:
        writer = csv.writer(f)
        writer.writerow(columns)
        try:
            while True:
                elapsed = time.perf_counter() - start
                writer.writerow(
                    [datetime.now().isoformat(timespec="milliseconds"), round(elapsed, 2)]
                    + [numeric_value(r) for r in responses]
                )
                f.flush()
                samples += 1
                live.update(_status_panel(path, samples, elapsed))
                responses = [connection.query(c) for c in commands]
        except KeyboardInterrupt:
            pass
    
    monitor_rows = read_monitors(session)
    if monitor_rows:
        mon_path = path.with_name(path.stem + "_mode6.csv")
        with mon_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(monitor_rows[0]))
            writer.writeheader()
            writer.writerows(monitor_rows)
        console.print(f"[green]Saved {len(monitor_rows)} mode 6 results to {mon_path}[/]")
    
    console.print(f"\n[green]Saved {samples} samples to {path}[/]")
    pause()