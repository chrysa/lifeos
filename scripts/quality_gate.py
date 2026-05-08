#!/usr/bin/env python3
"""Quality Gate Verification Script"""

from datetime import datetime
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


class QualityGate:
    CONFIG_FILE = ".quality-gate.json"
    BASELINE_FILE = ".quality-gate-baseline.json"

    def __init__(self):
        self.config_path = Path(self.CONFIG_FILE)
        self.baseline_path = Path(self.BASELINE_FILE)
        if not self.config_path.exists():
            print(f"❌ Configuration file not found: {self.CONFIG_FILE}")
            sys.exit(1)
        with open(self.config_path) as f:
            self.config = json.load(f)

    def _run(self, cmd: str) -> tuple[int, str]:
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)
            return result.returncode, result.stdout + result.stderr
        except subprocess.TimeoutExpired:
            return 124, "Command timed out after 300s"
        except Exception as e:
            return 127, f"Error: {e}"

    def _parse_coverage(self, output: str) -> float:
        for line in output.split("\n"):
            if "coverage" in line.lower():
                for word in line.split():
                    if word.endswith("%"):
                        try:
                            return float(word.rstrip("%"))
                        except ValueError:
                            continue
        return -1.0

    def _parse_passed_tests(self, output: str) -> int:
        for line in output.split("\n"):
            if "passed" in line:
                parts = line.split()
                for i, part in enumerate(parts):
                    if "passed" in part and i > 0:
                        try:
                            return int(parts[i - 1])
                        except (ValueError, IndexError):
                            continue
        return 0

    def _parse_warning_count(self, output: str) -> int:
        for line in output.split("\n"):
            if "warning" in line.lower():
                try:
                    count = int(line.split()[0])
                    return count
                except (ValueError, IndexError):
                    continue
        return 0

    def _parse_error_count(self, output: str) -> int:
        for line in output.split("\n"):
            if "error" in line.lower():
                try:
                    count = int(line.split()[0])
                    return count
                except (ValueError, IndexError):
                    continue
        return 0

    def _run_gate(self, gate_name: str, cmd: str) -> dict[str, Any]:
        print(f"  🔍 {gate_name}...", end=" ", flush=True)
        exit_code, output = self._run(cmd)
        result: dict[str, Any] = {
            "command": cmd,
            "exit_code": exit_code,
            "output": output,
            "timestamp": datetime.now().isoformat(),
        }

        if gate_name == "Tests":
            result["metric"] = self._parse_passed_tests(output)
            result["metric_name"] = "passed_tests"
        elif gate_name == "Coverage":
            result["metric"] = self._parse_coverage(output)
            result["metric_name"] = "coverage_percentage"
        elif gate_name == "Lint":
            result["metric"] = self._parse_warning_count(output)
            result["metric_name"] = "warning_count"
        elif gate_name == "Types":
            result["metric"] = self._parse_error_count(output)
            result["metric_name"] = "error_count"
        elif gate_name == "Build":
            result["metric"] = 0 if exit_code == 0 else 1
            result["metric_name"] = "build_status"

        print(f"OK ({result.get('metric', 'N/A')})")
        return result

    def baseline(self):
        print("\n📋 Recording Quality Gate Baseline\n")
        baseline_data = {"recorded_at": datetime.now().isoformat(), "gates": {}}
        gates = [
            ("Tests", self.config["commands"].get("tests", "make test")),
            ("Coverage", self.config["commands"].get("coverage", "make test-coverage")),
            ("Lint", self.config["commands"].get("lint", "make lint")),
            ("Types", self.config["commands"].get("types", "make type-check")),
            ("Build", self.config["commands"].get("build", "make build")),
        ]
        for gate_name, cmd in gates:
            result = self._run_gate(gate_name, cmd)
            baseline_data["gates"][gate_name] = result
        with open(self.baseline_path, "w") as f:
            json.dump(baseline_data, f, indent=2)
        print("\n✅ Baseline saved\n")
        return True

    def verify(self) -> bool:
        print("\n🔍 Verifying Quality Gates\n")
        if not self.baseline_path.exists():
            print("❌ Baseline not found. Run 'make quality-gate-baseline' first\n")
            return False
        with open(self.baseline_path) as f:
            baseline = json.load(f)
        gates = [
            ("Tests", self.config["commands"].get("tests", "make test"), "≥"),
            ("Coverage", self.config["commands"].get("coverage", "make test-coverage"), "≥"),
            ("Lint", self.config["commands"].get("lint", "make lint"), "="),
            ("Types", self.config["commands"].get("types", "make type-check"), "≤"),
            ("Build", self.config["commands"].get("build", "make build"), "="),
        ]
        print("Results:")
        print("-" * 60)
        all_passed = True
        for gate_name, cmd, check_type in gates:
            current = self._run_gate(gate_name, cmd)
            baseline_gate = baseline["gates"][gate_name]
            baseline_metric = baseline_gate.get("metric", 0)
            current_metric = current.get("metric", 0)
            passed = (
                (check_type == "=" and current_metric == baseline_metric)
                or (check_type == "≥" and current_metric >= baseline_metric)
                or (check_type == "≤" and current_metric <= baseline_metric)
            )
            status = "✅" if passed else "❌"
            print(f"{status} {gate_name:12} {baseline_metric} {check_type} {current_metric}")
            if not passed:
                all_passed = False
        print("-" * 60)
        if all_passed:
            print("\n✅ All gates passed\n")
            return True
        else:
            print("\n❌ Regression detected\n")
            return False


def main():
    if len(sys.argv) < 2:
        print("Usage: python quality_gate.py [baseline|verify]")
        sys.exit(1)
    command = sys.argv[1].lower()
    gate = QualityGate()
    if command == "baseline":
        sys.exit(0 if gate.baseline() else 1)
    elif command == "verify":
        sys.exit(0 if gate.verify() else 1)
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
