#!/usr/bin/env python3
"""Build a LittleFS image from the sketch data directory and flash it.

The image is written only to the partition LittleFS mounts (subtype spiffs
on the Arduino ESP32 core). The application partition is left alone.
"""

import argparse
import subprocess
import sys
from pathlib import Path


def parse_properties(text):
    props = {}
    for line in text.splitlines():
        if "=" not in line or line.startswith("["):
            continue
        key, value = line.split("=", 1)
        props[key.strip()] = value.strip()
    return props


def board_properties(cli, config, fqbn):
    command = [
        cli,
        "--config-file",
        config,
        "board",
        "details",
        "-b",
        fqbn,
        "--show-properties",
    ]
    try:
        completed = subprocess.run(command, check=True, capture_output=True, text=True)
    except FileNotFoundError:
        raise SystemExit(f"arduino-cli not found at {cli}. Run `make bootstrap` first.")
    except subprocess.CalledProcessError as exc:
        # Options after the third colon can be rejected by older CLI builds.
        if ":" in fqbn:
            base = fqbn.split(":")
            if len(base) > 3:
                short = ":".join(base[:3])
                return board_properties(cli, config, short)
        sys.stderr.write(exc.stderr or exc.stdout or "")
        raise SystemExit(exc.returncode)
    return parse_properties(completed.stdout)


def read_data_dir(config_path):
    for line in Path(config_path).read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("data:"):
            return Path(stripped.split(":", 1)[1].strip())
    return Path(".arduino/data")


def newest_tool(data_dir, tool_name, binary_names):
    root = data_dir / "packages" / "esp32" / "tools" / tool_name
    if not root.is_dir():
        return None
    versions = sorted((path for path in root.iterdir() if path.is_dir()), key=lambda path: path.name)
    for version in reversed(versions):
        found = find_binary(version, binary_names)
        if found:
            return found
    return None


def find_binary(directory, names):
    directory = Path(directory)
    if not directory.is_dir():
        return None
    for name in names:
        direct = directory / name
        if direct.is_file():
            return direct
    for name in names:
        for candidate in directory.rglob(name):
            if candidate.is_file():
                return candidate
    return None


def tool_binary(props, data_dir, prop_key, package_name, binary_names):
    path = props.get(prop_key)
    if path:
        found = find_binary(Path(path), binary_names)
        if found:
            return found
    found = newest_tool(data_dir, package_name, binary_names)
    if found:
        return found
    raise SystemExit(
        f"Could not find {' or '.join(binary_names)} "
        f"(property {prop_key}). Run `make bootstrap`."
    )


def spiffs_partition(build_dir):
    candidates = list(Path(build_dir).rglob("partitions.csv"))
    if not candidates:
        raise SystemExit(
            f"No partitions.csv under {build_dir}. Compile the ESP32 sketch first."
        )
    chosen = None
    for path in candidates:
        for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
            line = raw.split("#", 1)[0].strip()
            if not line:
                continue
            fields = [field.strip() for field in line.split(",")]
            if len(fields) < 5:
                continue
            name, _kind, subtype, offset, size = fields[:5]
            if subtype != "spiffs":
                continue
            entry = (name, int(offset, 0), int(size, 0), path)
            chosen = entry
            if name == "spiffs":
                return chosen
    if chosen is None:
        raise SystemExit(f"No spiffs partition in {candidates[0]}")
    return chosen


def run(command):
    print("+ " + " ".join(str(part) for part in command), flush=True)
    subprocess.run([str(part) for part in command], check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cli", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--fqbn", required=True)
    parser.add_argument("--build-dir", required=True)
    parser.add_argument("--data", required=True)
    parser.add_argument("--port", required=True)
    parser.add_argument("--baud", type=int, default=921600)
    args = parser.parse_args()

    data = Path(args.data)
    if not data.is_dir():
        raise SystemExit(f"LittleFS data directory not found: {data}")

    _name, offset, size, partition_file = spiffs_partition(args.build_dir)
    image = Path(args.build_dir) / "littlefs.bin"
    props = board_properties(args.cli, args.config, args.fqbn)
    data_dir = read_data_dir(args.config)
    mklittlefs = tool_binary(
        props,
        data_dir,
        "runtime.tools.mklittlefs.path",
        "mklittlefs",
        ["mklittlefs", "mklittlefs.exe"],
    )
    esptool = tool_binary(
        props,
        data_dir,
        "runtime.tools.esptool_py.path",
        "esptool_py",
        ["esptool", "esptool.py", "esptool.exe"],
    )

    print(
        f"LittleFS partition {hex(offset)} size {size} bytes ({partition_file})",
        flush=True,
    )
    run([mklittlefs, "-c", data, "-p", "256", "-b", "4096", "-s", str(size), image])

    if esptool.name == "esptool.py":
        command = [sys.executable, esptool]
    else:
        command = [esptool]
    command += [
        "--chip",
        "esp32",
        "--port",
        args.port,
        "--baud",
        str(args.baud),
        "write-flash",
        "--flash-mode",
        "keep",
        "--flash-size",
        "keep",
        hex(offset),
        image,
    ]
    run(command)


if __name__ == "__main__":
    main()
