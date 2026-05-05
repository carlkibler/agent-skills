#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Run a command locally and on SSH hosts, then compare exit status and output."""

from __future__ import annotations

import argparse
import json
import re
import shlex
import subprocess
from dataclasses import asdict, dataclass


@dataclass
class Result:
    label: str
    command: str
    returncode: int
    stdout: str
    stderr: str


def strip_noise(text: str) -> str:
    text = text.replace("\x1bc", "")
    text = re.sub(r"stty: stdin isn't a terminal\s*", "", text)
    return text.strip()


def run(label: str, cmd: list[str], timeout: int) -> Result:
    proc = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout, check=False)
    return Result(label=label, command=" ".join(shlex.quote(part) for part in cmd), returncode=proc.returncode, stdout=strip_noise(proc.stdout), stderr=strip_noise(proc.stderr))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", action="append", default=[], help="SSH host to compare. Repeatable.")
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("command", nargs=argparse.REMAINDER, help="Command after --")
    args = parser.parse_args()

    command = args.command
    if command and command[0] == "--":
        command = command[1:]
    if not command:
        parser.error("provide a command after --")

    results = [run("local", command, args.timeout)]
    quoted = " ".join(shlex.quote(part) for part in command)
    for host in args.host:
        results.append(run(host, ["ssh", host, "bash", "-lc", quoted], args.timeout))

    ok = all(result.returncode == 0 for result in results)
    if args.json:
        print(json.dumps({"ok": ok, "results": [asdict(result) for result in results]}, indent=2))
    else:
        for result in results:
            print(f"## {result.label} — exit {result.returncode}")
            print(f"$ {result.command}")
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print("stderr:")
                print(result.stderr)
            print()
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
