# OBD Scanner - By Benjamin Diaz

A terminal OBD-II scanner written in Python. It reads trouble codes, freeze frame data and live sensor data from your car, and records driving data which is later exported into a CSV for data analytics.

## Features

- **Check / erase codes**: shows stored and pending trouble codes (DTCs) with descriptions. Erasing requires confirmation.
- **Freeze frame**: shows the snapshot of sensor values saved when a code was set.
- **Live data table**: a continuously updating table of every parameter your car answers.
- **Drive data collection**: records live data to a timestamped CSV while you drive. A live view on screen lets a passenger watch the values.
- **Auto-discovery**: on startup the app tests every command it knows in modes 1, 2 and 6, keeps the ones your car answers, and ignores the rest for the session.
- **Mode 6 export**: when a drive recording stops, the car's self-test results (measured value, limits, pass/fail) are saved to a second CSV.
  - See more about Mode 6 on the OBD library docs
- **Demo mode**: runs the full interface against a simulated car, with no cable needed.

## Requirements

- Python 3.9 or newer
- An ELM327-based OBD-to-USB cable (most generic cables). Some brand-specific cables, such as VAG KKL cables, are not ELM327 and will not work.
- Windows, Linux or macOS. Tested on Windows. Windows may need the cable's driver (FTDI or CH340, depending on its chip).

Dependencies (installed automatically): `obd`, `rich`.

## Install

This project uses [uv](https://docs.astral.sh/uv/).

```
# Clone the repo and cd into its folder
uv venv .venv
.venv\Scripts\activate          # Linux/macOS: source .venv/bin/activate
uv pip install -r pyproject.toml
```

## Usage

Plug the cable into the car and the computer, turn the ignition on, then run:

```
python -m obdscan
```

Codes and freeze frame work with the ignition on and the engine off. Live data is only meaningful with the engine running.

To try the interface without a car:

```
python -m obdscan --demo
```

## Output

Recordings are saved in a `logs/` folder next to where you run the app:

| File | Content |
|---|---|
| `drive_YYYYMMDD_HHMMSS.csv` | One row per sample: timestamp, elapsed seconds, and one column per parameter. Units are in the column header. Missing readings are blank. |
| `drive_YYYYMMDD_HHMMSS_mode6.csv` | One row per mode 6 test: monitor, test, value, min, max, passed. Read once when the recording stops. |

Both files load directly into pandas or Excel.

## Project layout

```
obdscan/
  __main__.py      menu and program entry point
  connection.py    port selection, connection, command discovery, mode 6 reading
  dtc.py           read and erase trouble codes
  freeze_frame.py  freeze frame screen
  live.py          live data table
  logger.py        drive recording to CSV
  demo.py          simulated car for --demo
  ui.py            shared console and formatting helpers
```

## Limitations

- Only commands defined in the `python-obd` library are probed. Manufacturer-specific data (mode 22) is not supported.
- Discovery can take from tens of seconds to a couple of minutes, because every unsupported command waits for a timeout.
- Each parameter is a separate request to the car, so more parameters means fewer samples per second. The sample rate depends on your car and cable.
- Some live values that are not a single number (for example the readiness monitor status) are skipped.
- Cheap clone cables may return no data for some commands, especially freeze frame.
- Mode 6 values are raw and often need the manufacturer's documentation to interpret.
- Demo mode tests the interface only. It does not reproduce real car communication.

## Safety

- Erasing codes also erases the freeze frame and resets the car's emissions readiness monitors. Some regions require those monitors to be complete for an emissions inspection. Read and note your codes before erasing.
- Do not operate the app while driving. Have a passenger watch the screen or use it only for recording.
- Use at your own risk. This software only sends standard read commands, plus the erase command when you confirm it, but the author is not responsible for any effect on your vehicle.

## Disclaimer

Not affiliated with any vehicle manufacturer or with the `python-obd` project.

## License

<choose a license, for example MIT>
