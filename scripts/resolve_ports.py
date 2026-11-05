#!/usr/bin/env python3
"""Pick the Nano and ESP32 serial ports from `arduino-cli board list`.

With --print, the chosen port is written to stdout and diagnostics go to
stderr. NANO_PORT and ESP_PORT, when already set, are used as-is.
"""

import argparse
import json
import os
import subprocess
import sys


def normalize_id(value):
    if not value:
        return ""
    text = str(value).strip().upper()
    if text.startswith("0X"):
        text = text[2:]
    return text


def parse_hardware_id(hardware_id):
    if not hardware_id or ":" not in str(hardware_id):
        return "", ""
    vid, pid = str(hardware_id).split(":", 1)
    return normalize_id(vid), normalize_id(pid)


def classify(fqbns, vid, pid):
    """Return 'nano', 'esp', or 'unknown'."""
    joined = " ".join(fqbns).lower()
    if "esp32:esp32" in joined:
        return "esp"
    if "arduino:avr:nano" in joined:
        return "nano"
    vid = normalize_id(vid)
    pid = normalize_id(pid)
    # CP2102 is the common ESP32 Dev Module UART. 303A is Espressif native USB.
    if vid == "303A" or (vid == "10C4" and pid == "EA60"):
        return "esp"
    # 2341 is official Arduino. FTDI 0403:6001 is a common genuine Nano adapter.
    if vid == "2341" or (vid == "0403" and pid == "6001"):
        return "nano"
    return "unknown"


def load_ports(cli, config):
    command = [cli, "--config-file", config, "board", "list", "--format", "json"]
    try:
        completed = subprocess.run(command, check=True, capture_output=True, text=True)
    except FileNotFoundError:
        raise SystemExit(f"arduino-cli not found at {cli}. Run `make bootstrap` first.")
    except subprocess.CalledProcessError as exc:
        sys.stderr.write(exc.stderr or "")
        raise SystemExit(exc.returncode)

    try:
        payload = json.loads(completed.stdout or "[]")
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Could not parse `arduino-cli board list` JSON: {exc}")

    if isinstance(payload, dict):
        entries = payload.get("detected_ports") or payload.get("ports") or []
    elif isinstance(payload, list):
        entries = payload
    else:
        entries = []

    ports = []
    for entry in entries:
        port_info = entry.get("port") if isinstance(entry.get("port"), dict) else entry
        if not isinstance(port_info, dict):
            continue
        protocol = (port_info.get("protocol") or entry.get("protocol") or "serial").lower()
        if protocol not in ("serial", ""):
            continue
        address = port_info.get("address") or port_info.get("label") or entry.get("address")
        if not address:
            continue
        properties = port_info.get("properties") or {}
        vid = properties.get("vid") or ""
        pid = properties.get("pid") or ""
        if not vid or not pid:
            parsed_vid, parsed_pid = parse_hardware_id(port_info.get("hardware_id", ""))
            vid = vid or parsed_vid
            pid = pid or parsed_pid
        boards = entry.get("matching_boards")
        if boards is None:
            boards = entry.get("boards") or []
        fqbns = [board.get("fqbn") for board in (boards or []) if board.get("fqbn")]
        ports.append(
            {
                "address": address,
                "vid": normalize_id(vid),
                "pid": normalize_id(pid),
                "fqbns": fqbns,
                "role": classify(fqbns, vid, pid),
            }
        )
    return ports


def format_port(port):
    ident = f"{port['vid']}:{port['pid']}" if port["vid"] or port["pid"] else "no-id"
    return f"  {port['address']}  {ident}  {port['role']}"


def fail(message, ports):
    lines = [message, "Ports seen:"]
    if ports:
        lines.extend(format_port(port) for port in ports)
    else:
        lines.append("  (none)")
    lines.append("Set the port yourself, for example:")
    lines.append("  make flash NANO_PORT=/dev/ttyUSB0 ESP_PORT=/dev/ttyUSB1")
    raise SystemExit("\n".join(lines))


def resolve(ports, need):
    result = {}
    if need in ("nano", "both") and os.environ.get("NANO_PORT"):
        result["nano"] = os.environ["NANO_PORT"]
    if need in ("esp", "both") and os.environ.get("ESP_PORT"):
        result["esp"] = os.environ["ESP_PORT"]

    wanted = ["nano", "esp"] if need == "both" else [need]
    if all(role in result for role in wanted):
        return result

    used = set(result.values())
    available = [port for port in ports if port["address"] not in used]

    for role in wanted:
        if role in result:
            continue
        hits = [port for port in available if port["role"] == role]
        if len(hits) > 1:
            fail(f"More than one port looks like the {role}.", ports)
        if len(hits) == 1:
            result[role] = hits[0]["address"]
            available.remove(hits[0])

    missing = [role for role in wanted if role not in result]
    unknowns = [port for port in available if port["role"] == "unknown"]
    # A single leftover CH340 (or other unrecognized adapter) can fill the
    # one role that is still open, including when the other board was identified.
    if len(missing) == 1 and len(unknowns) == 1:
        result[missing[0]] = unknowns[0]["address"]
        missing = []

    if missing:
        if need == "both" and ports and all(port["role"] == "unknown" for port in ports):
            fail(
                "Both serial ports look alike (often two CH340 adapters). "
                "Pass NANO_PORT and ESP_PORT.",
                ports,
            )
        fail(
            "Could not tell which serial port belongs to the " + " and ".join(missing) + ".",
            ports,
        )
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cli", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--need", choices=("nano", "esp", "both"), required=True)
    parser.add_argument(
        "--print",
        dest="print_port",
        action="store_true",
        help="print only the requested port (requires --need nano or esp)",
    )
    args = parser.parse_args()
    if args.print_port and args.need == "both":
        raise SystemExit("--print needs --need nano or --need esp")

    wanted = ["nano", "esp"] if args.need == "both" else [args.need]
    env_names = {"nano": "NANO_PORT", "esp": "ESP_PORT"}
    if all(os.environ.get(env_names[role]) for role in wanted):
        chosen = {role: os.environ[env_names[role]] for role in wanted}
    else:
        chosen = resolve(load_ports(args.cli, args.config), args.need)

    if args.print_port:
        sys.stdout.write(chosen[args.need] + "\n")
        return
    if args.need in ("nano", "both"):
        sys.stdout.write(f"NANO_PORT={chosen['nano']}\n")
    if args.need in ("esp", "both"):
        sys.stdout.write(f"ESP_PORT={chosen['esp']}\n")


if __name__ == "__main__":
    main()
