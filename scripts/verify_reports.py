"""Verify consumer outcomes without ever importing target fixture code."""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys


def scan(path: Path, *, threshold: str = "high", report_format: str = "json"):
    result = subprocess.run(
        ["hermes-plugin-guard", "scan", str(path), "--fail-on", threshold,
         "--format", report_format],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    return result


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    expected = {
        "CLEAN_OUTCOME": "success",
        "RISKY_OUTCOME": "failure",
        "INFORMATIONAL_OUTCOME": "success",
        "MISSING_OUTCOME": "failure",
    }
    for name, outcome in expected.items():
        require(os.environ.get(name) == outcome,
                f"{name}: expected {outcome}, got {os.environ.get(name)!r}")

    require(sys.version_info[:2] == (3, 11), "Action must select Python 3.11")
    safe = Path("samples/safe_plugin")
    risky = Path("samples/risky plugin")
    clean = scan(safe)
    require(clean.returncode == 0, f"Clean scan failed: {clean.stderr}")
    require(json.loads(clean.stdout)["summary"]["findings"] == 0,
            "Clean fixture must have zero findings")
    dangerous = scan(risky)
    require(dangerous.returncode == 1, "Critical findings must return exit 1")
    payload = json.loads(dangerous.stdout)
    require("HPG101" in {f["rule_id"] for f in payload["findings"]},
            "Dynamic execution rule must be present")
    informational = scan(risky, threshold="none")
    require(informational.returncode == 0, "Report-only mode must return exit 0")
    require(json.loads(informational.stdout)["summary"]["findings"] > 0,
            "Report-only mode must retain findings")
    repeat = scan(risky, threshold="none")
    require(repeat.stdout == informational.stdout, "JSON output must be deterministic")
    missing = scan(Path("samples/not-present"))
    require(missing.returncode == 2, "Missing target must return exit 2")
    sarif = scan(risky, threshold="none", report_format="sarif")
    require(sarif.returncode == 0, f"SARIF scan failed: {sarif.stderr}")
    require(json.loads(sarif.stdout)["version"] == "2.1.0", "Invalid SARIF version")
    require(not list(Path("samples").rglob("EXECUTED")), "Target code was executed")
    print("PASS: clean, critical, report-only, missing target, JSON, SARIF, "
          "determinism, Python 3.11 and no target execution")


if __name__ == "__main__":
    main()
