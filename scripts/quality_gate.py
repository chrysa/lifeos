#!/usr/bin/env python3
"""Quality Gate Verification Script.

Machine-readable output lines:
- GATE_RESULT|<Gate>|PASS|...
- GATE_RESULT|<Gate>|FAIL|...
- OVERALL_RESULT|PASS
- OVERALL_RESULT|FAIL
"""

import json
import re
import subprocess  # nosec B404
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

_OVERALL_PASS = "OVERALL_RESULT|PASS"
_OVERALL_FAIL = "OVERALL_RESULT|FAIL"


class QualityGate:
    CONFIG_FILE = ".quality-gate.json"
    BASELINE_FILE = ".quality-gate-baseline.json"
    LAST_REPORT_FILE = ".quality-gate-last-report.json"

    def __init__(self) -> None:
        self.config_path = Path(self.CONFIG_FILE)
        self.baseline_path = Path(self.BASELINE_FILE)
        self.last_report_path = Path(self.LAST_REPORT_FILE)

        if not self.config_path.exists():
            print(f"ERROR: configuration file not found: {self.CONFIG_FILE}")  # print-detection: disable
            sys.exit(1)

        with open(self.config_path, encoding="utf-8") as handle:
            self.config = json.load(handle)

        self.gates = [
            ("Tests", "tests", "passed_tests", "≥", "make test"),
            ("Coverage", "coverage", "coverage_percentage", "≥", "make test-coverage"),
            ("Lint", "lint", "warning_count", "=", "make lint"),
            ("Types", "types", "error_count", "≤", "make type-check"),
            ("Build", "build", "build_status", "=", "make build"),
            (
                "Secrets",
                "security_secrets",
                "secret_count",
                "=",
                "detect-secrets scan --all-files 2>&1 || true",
            ),
            (
                "VulnDeps",
                "security_vulns",
                "vuln_count",
                "≤",
                "pip-audit 2>&1 || npm audit --audit-level=high 2>&1 || true",
            ),
        ]

    def _run(self, cmd: str) -> tuple[int, str]:
        try:
            result = subprocess.run(  # nosec B602 B603
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=600,
            )
            return result.returncode, (result.stdout or "") + (result.stderr or "")
        except subprocess.TimeoutExpired:
            return 124, "Command timed out after 600 seconds"
        except Exception as exc:
            return 127, f"Execution error: {exc}"

    def _parse_passed_tests(self, output: str) -> int:
        patterns = [
            r"(\d+)\s+passed",
            r"passed\s*=\s*(\d+)",
        ]
        for pattern in patterns:
            match = re.search(pattern, output, flags=re.IGNORECASE)
            if match:
                return int(match.group(1))
        return 0

    # Coverage summary lines, in order of trust. Anchored on purpose: a loose
    # "any line mentioning coverage" scan matches pytest's own verbose progress
    # (`… ::test_service_named_dev_is_covered PASSED [ 13%]`) and reports the
    # progress percentage as the coverage figure.
    COVERAGE_PATTERNS = (
        r"^TOTAL\s+.*?(\d+(?:\.\d+)?)%",  # pytest-cov / coverage term report
        r"Total coverage:\s*(\d+(?:\.\d+)?)%",  # --cov-fail-under summary line
        r"All files\s*\|\s*(\d+(?:\.\d+)?)",  # jest / istanbul text summary
        r"^Statements\s*:\s*(\d+(?:\.\d+)?)%",  # nyc text-summary
    )

    def _parse_coverage(self, output: str) -> float:
        for pattern in self.COVERAGE_PATTERNS:
            match = re.search(pattern, output, flags=re.IGNORECASE | re.MULTILINE)
            if match:
                try:
                    return float(match.group(1))
                except ValueError:
                    continue
        return self._parse_coverage_report()

    def _parse_coverage_report(self) -> float:
        """Read the coverage percentage from a written XML report.

        `make test-cov` may emit only `--cov-report=xml`, in which case stdout
        carries no summary at all and the textual patterns above find nothing.
        """
        for candidate in (Path("reports/coverage.xml"), Path("coverage.xml")):
            if not candidate.is_file():
                continue
            match = re.search(
                r'<coverage[^>]*\bline-rate="([0-9.]+)"',
                candidate.read_text(encoding="utf-8", errors="replace"),
            )
            if match:
                try:
                    return round(float(match.group(1)) * 100, 2)
                except ValueError:
                    continue
        return -1.0

    def _parse_warning_count(self, output: str) -> int:
        match = re.search(r"(\d+)\s+warnings?", output, flags=re.IGNORECASE)
        if match:
            return int(match.group(1))
        return 0

    def _parse_error_count(self, output: str) -> int:
        match = re.search(r"(\d+)\s+errors?", output, flags=re.IGNORECASE)
        if match:
            return int(match.group(1))
        return 0

    def _parse_secret_count(self, output: str) -> int:
        try:
            d = json.loads(output)
            return sum(len(v) for v in d.get("results", {}).values())
        except (json.JSONDecodeError, AttributeError, ValueError):
            pass
        match = re.search(r"secrets?\s+found[:\s]+(\d+)", output, re.IGNORECASE)
        if match:
            return int(match.group(1))
        return 0

    def _parse_vuln_count(self, output: str) -> int:
        match = re.search(r"found\s+(\d+)\s+vulnerabilit", output, re.IGNORECASE)
        if match:
            return int(match.group(1))
        count = len(re.findall(r"(?:GHSA|CVE)-\S+", output))
        if count:
            return count
        if re.search(r"no\s+known\s+vulnerabilit", output, re.IGNORECASE):
            return 0
        return 0

    def _parse_metric(self, gate_name: str, exit_code: int, output: str) -> Any:
        # Build is the only gate whose metric comes from the exit code rather
        # than the output, so it stays out of the table.
        if gate_name == "Build":
            return 0 if exit_code == 0 else 1
        parsers = {
            "Tests": self._parse_passed_tests,
            "Coverage": self._parse_coverage,
            "Lint": self._parse_warning_count,
            "Types": self._parse_error_count,
            "Secrets": self._parse_secret_count,
            "VulnDeps": self._parse_vuln_count,
        }
        parser = parsers.get(gate_name)
        return parser(output) if parser else None

    def _compare(self, current: Any, target: Any, operator: str) -> bool:
        if operator == "=":
            return current == target
        if operator == "≥":
            return current >= target
        if operator == "≤":
            return current <= target
        if operator == ">=":
            return current >= target
        if operator == "<=":
            return current <= target
        return False

    def _run_gate(
        self, gate_name: str, key: str, metric_name: str, default_cmd: str
    ) -> dict[str, Any]:
        cmd = self.config.get("commands", {}).get(key, default_cmd)
        print(f"RUN_GATE|{gate_name}|{cmd}")  # print-detection: disable
        exit_code, output = self._run(cmd)
        metric = self._parse_metric(gate_name, exit_code, output)
        return {
            "gate": gate_name,
            "command": cmd,
            "exit_code": exit_code,
            "metric_name": metric_name,
            "metric": metric,
            "timestamp": datetime.now().isoformat(),
            "output": output,
        }

    def _write_report(self, report: dict[str, Any]) -> None:
        with open(self.last_report_path, "w", encoding="utf-8") as handle:
            json.dump(report, handle, indent=2)

    def baseline(self) -> bool:
        print("BASELINE|START")  # print-detection: disable
        baseline_data: dict[str, Any] = {
            "recorded_at": datetime.now().isoformat(),
            "gates": {},
            "valid": True,
        }

        all_ok = True
        for gate_name, key, metric_name, _default_op, default_cmd in self.gates:
            result = self._run_gate(gate_name, key, metric_name, default_cmd)
            baseline_data["gates"][gate_name] = result
            if result["exit_code"] != 0:
                all_ok = False
                baseline_data["valid"] = False
            status = "PASS" if result["exit_code"] == 0 else "FAIL"
            print(  # print-detection: disable
                f"GATE_RESULT|{gate_name}|{status}|metric={result['metric']}|"
                f"exit={result['exit_code']}|mode=baseline"
            )

        with open(self.baseline_path, "w", encoding="utf-8") as handle:
            json.dump(baseline_data, handle, indent=2)

        report = {
            "mode": "baseline",
            "overall": "PASS" if all_ok else "FAIL",
            "baseline_file": str(self.baseline_path),
            "gates": baseline_data["gates"],
        }
        self._write_report(report)

        if all_ok:
            print(_OVERALL_PASS)  # print-detection: disable
            return True

        print(_OVERALL_FAIL)  # print-detection: disable
        print(  # print-detection: disable
            "ERROR: baseline contains failing gates; fix quality checks before using this baseline"
        )
        return False

    def _evaluate_gate_result(
        self,
        baseline_valid: bool,
        current: dict[str, Any],
        current_metric: Any,
        target: Any,
        operator: str,
    ) -> tuple[bool, str]:
        """Return (passed, reason) for a single gate evaluation."""
        if not baseline_valid:
            return False, "invalid_baseline"
        if current.get("exit_code", 1) != 0:
            return False, "command_failed"
        try:
            passed = self._compare(current_metric, target, operator)
            return passed, "ok" if passed else "metric_regression"
        except Exception:
            return False, "comparison_error"

    def verify(self) -> bool:
        print("VERIFY|START")  # print-detection: disable
        if not self.baseline_path.exists():
            report = {
                "mode": "verify",
                "overall": "FAIL",
                "reason": "missing_baseline",
                "baseline_file": str(self.baseline_path),
            }
            self._write_report(report)
            print(_OVERALL_FAIL)  # print-detection: disable
            print("ERROR: baseline file not found; run quality-gate-baseline first")  # print-detection: disable
            return False

        with open(self.baseline_path, encoding="utf-8") as handle:
            baseline = json.load(handle)

        baseline_valid = bool(baseline.get("valid", True))
        all_passed = True
        gate_reports: list[dict[str, Any]] = []

        for gate_name, key, metric_name, default_op, default_cmd in self.gates:
            current = self._run_gate(gate_name, key, metric_name, default_cmd)
            baseline_gate = baseline.get("gates", {}).get(gate_name, {})

            threshold_cfg = self.config.get("thresholds", {}).get(key, {})
            operator = str(threshold_cfg.get("operator", default_op))
            baseline_metric = baseline_gate.get("metric", 0)
            target = threshold_cfg.get("value", baseline_metric)
            current_metric = current.get("metric", 0)

            passed, reason = self._evaluate_gate_result(
                baseline_valid, current, current_metric, target, operator
            )
            if not passed:
                all_passed = False

            status = "PASS" if passed else "FAIL"
            print(  # print-detection: disable
                f"GATE_RESULT|{gate_name}|{status}|baseline={baseline_metric}|"
                f"target={target}|current={current_metric}|op={operator}|"
                f"exit={current.get('exit_code', 1)}|reason={reason}"
            )

            gate_reports.append(
                {
                    "gate": gate_name,
                    "status": status,
                    "reason": reason,
                    "operator": operator,
                    "baseline_metric": baseline_metric,
                    "target": target,
                    "current_metric": current_metric,
                    "exit_code": current.get("exit_code", 1),
                    "metric_name": metric_name,
                    "command": current.get("command", ""),
                }
            )

        report = {
            "mode": "verify",
            "overall": "PASS" if all_passed else "FAIL",
            "baseline_file": str(self.baseline_path),
            "generated_at": datetime.now().isoformat(),
            "gates": gate_reports,
        }
        self._write_report(report)

        if all_passed:
            print(_OVERALL_PASS)  # print-detection: disable
            return True

        print(_OVERALL_FAIL)  # print-detection: disable
        return False


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 quality_gate.py [baseline|verify]")  # print-detection: disable
        sys.exit(1)

    command = sys.argv[1].strip().lower()
    quality_gate = QualityGate()

    if command == "baseline":
        sys.exit(0 if quality_gate.baseline() else 1)
    if command == "verify":
        sys.exit(0 if quality_gate.verify() else 1)

    print(f"Unknown command: {command}")  # print-detection: disable
    sys.exit(1)


if __name__ == "__main__":
    main()
