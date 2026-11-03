#!/usr/bin/env python3
"""Quality Gate Verification Script.

Machine-readable output lines:
- GATE_RESULT|<Gate>|PASS|...
- GATE_RESULT|<Gate>|FAIL|...
- OVERALL_RESULT|PASS
- OVERALL_RESULT|FAIL
- OVERALL_RESULT|SKIP  (verify only: no baseline, nothing was evaluated)

Exit codes:
- 0  every gate passed
- 1  a gate failed, the baseline is invalid, or the usage is wrong
- 2  ``verify`` evaluated nothing (no baseline). Never 0: "not evaluated" is not "green".
"""

from __future__ import annotations

import json
import re
import shlex
import shutil
import subprocess
import sys
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

# shutil.which found nothing — the shell's own "command not found" status.
_EXIT_NOT_FOUND = 127
# No alternative applied: every one was guarded by a manifest this repo lacks.
_EXIT_NOT_APPLICABLE = 126

# Process exit codes of the CLI. NOT_EVALUATED is distinct from both PASS and FAIL:
# a verify run without a baseline checked nothing, and exiting 0 made every repo
# without a baseline look green (the "false green" this code exists to prevent).
EXIT_PASS = 0
EXIT_FAIL = 1
EXIT_NOT_EVALUATED = 2

# Operator -> comparison, as a table. Both the unicode and ASCII spellings of each
# ordering are accepted because baselines exist carrying either. An operator absent
# from this table compares False: an unrecognised gate must never pass by default.
_COMPARISONS: dict[str, Callable[[Any, Any], bool]] = {
    "=": lambda current, target: bool(current == target),
    "≥": lambda current, target: bool(current >= target),
    ">=": lambda current, target: bool(current >= target),
    "≤": lambda current, target: bool(current <= target),
    "<=": lambda current, target: bool(current <= target),
}


@dataclass(frozen=True)
class CommandSpec:
    """An ordered fallback chain of argv vectors, run without a shell.

    Each alternative is executed in order until one exits 0. This replaces the
    previous ``shell=True`` single-string form: shell operators such as ``||``
    are no longer interpreted by a shell — fallbacks are expressed as multiple
    argv vectors instead. ``swallow_exit`` mirrors a trailing ``|| true``: the
    gate is then driven by its parsed metric rather than the tool's exit code.
    """

    alternatives: tuple[tuple[str, ...], ...]
    swallow_exit: bool = False
    # Per-alternative manifest guard, aligned by index. ``None`` means always
    # applicable. An alternative whose manifest is absent is skipped rather than
    # run: npm audit in a repo with no package.json finds nothing and reports it
    # as zero vulnerabilities, which answers a Python question by asking npm.
    requires: tuple[str | None, ...] = ()

    @classmethod
    def parse(cls, raw: object, *, swallow_exit: bool = False) -> CommandSpec:
        """Build a spec from a config override.

        Accepted forms:
        - ``"make lint"`` → one argv vector (split with shlex, never a shell).
        - ``["make", "lint"]`` → one argv vector.
        - ``[["pip-audit"], ["npm", "audit"]]`` → an ordered fallback chain.
        - ``[{"cmd": ["npm", "audit"], "requires": "package.json"}]`` → the same,
          each alternative guarded by a manifest that must exist for it to apply.
        """
        if isinstance(raw, str):
            return cls((tuple(shlex.split(raw)),), swallow_exit=swallow_exit)
        if isinstance(raw, list):
            if raw and all(isinstance(item, str) for item in raw):
                return cls((tuple(raw),), swallow_exit=swallow_exit)
            chain: list[tuple[str, ...]] = []
            guards: list[str | None] = []
            for alt in raw:
                if isinstance(alt, dict):
                    argv = alt.get("cmd")
                    if not isinstance(argv, (list, tuple)):
                        raise ValueError(f"Alternative needs a 'cmd' list: {alt!r}")
                    chain.append(tuple(str(part) for part in argv))
                    guard = alt.get("requires")
                    guards.append(str(guard) if guard is not None else None)
                    continue
                if not isinstance(alt, (list, tuple)):
                    raise ValueError(f"Unsupported command specification: {raw!r}")
                chain.append(tuple(str(part) for part in alt))
                guards.append(None)
            return cls(tuple(chain), swallow_exit=swallow_exit, requires=tuple(guards))
        raise ValueError(f"Unsupported command specification: {raw!r}")

    def guard_for(self, index: int) -> str | None:
        """The manifest guarding alternative ``index``, if it declares one."""
        return self.requires[index] if index < len(self.requires) else None

    def display(self) -> str:
        rendered = " || ".join(shlex.join(alt) for alt in self.alternatives)
        return f"{rendered} || true" if self.swallow_exit else rendered


# One row per gate: display name, config key, metric name, comparison operator,
# and the command to run when the config overrides nothing. Module-level data
# rather than construction, so the defaults are inspectable — and testable —
# without a .quality-gate.json on disk.
GateSpec = tuple[str, str, str, str, "CommandSpec"]

DEFAULT_GATES: list[GateSpec] = [
    ("Tests", "tests", "passed_tests", "≥", CommandSpec((("make", "test"),))),
    ("Coverage", "coverage", "coverage_percentage", "≥", CommandSpec((("make", "test-cov"),))),
    ("Lint", "lint", "warning_count", "=", CommandSpec((("make", "lint"),))),
    ("Types", "types", "error_count", "≤", CommandSpec((("make", "typecheck"),))),
    ("Build", "build", "build_status", "=", CommandSpec((("make", "build"),))),
    (
        "Secrets",
        "security_secrets",
        "secret_count",
        # ≤, not =: the metric counts findings the repo has NOT acknowledged in its
        # .secrets.baseline (see _parse_secret_count). Fewer of them is an improvement;
        # under = a removed or newly-audited finding failed the gate as a "regression".
        "≤",
        # NOT --all-files: that scans the working *directory*, and Tests and
        # Coverage run before this gate in the same job, writing coverage.xml and
        # report files into it. The metric then measures partly the run instead of
        # the code — it reported 111 against a baseline of 110 for a commit whose
        # tracked tree measured 110 exactly. Without the flag detect-secrets scans
        # what git tracks, which is what the baseline describes.
        # The baseline file itself is excluded with a fixed pattern (never one read
        # from the repo): its hashed_secret lines are flagged as hex high-entropy
        # strings and secret keywords, two findings per acknowledged entry, so
        # acknowledging a false positive raised the count instead of lowering it.
        CommandSpec(
            (("detect-secrets", "scan", "--exclude-files", r"^\.secrets\.baseline$"),),
            swallow_exit=True,
        ),
    ),
    (
        "VulnDeps",
        "security_vulns",
        "vuln_count",
        "≤",
        CommandSpec(
            (("pip-audit",), ("npm", "audit", "--audit-level=high")),
            swallow_exit=True,
        ),
    ),
]


class QualityGate:
    CONFIG_FILE = ".quality-gate.json"
    BASELINE_FILE = ".quality-gate-baseline.json"
    LAST_REPORT_FILE = ".quality-gate-last-report.json"
    # detect-secrets' own baseline: findings listed there are known (audited or
    # accepted) and must not count against the gate. Read only — never rewritten.
    SECRETS_BASELINE_FILE = ".secrets.baseline"

    def __init__(self) -> None:
        self.config_path = Path(self.CONFIG_FILE)
        self.baseline_path = Path(self.BASELINE_FILE)
        self.last_report_path = Path(self.LAST_REPORT_FILE)

        if not self.config_path.exists():
            print(f"ERROR: configuration file not found: {self.CONFIG_FILE}")
            sys.exit(1)

        with open(self.config_path, encoding="utf-8") as handle:
            self.config = json.load(handle)

        self.gates: list[GateSpec] = list(DEFAULT_GATES)
        # Start time of the gate command being run (set by _run_gate); None outside a run.
        self._gate_started_at: float | None = None

    def _execute(self, executable: str, argv: list[str]) -> tuple[int, str, bool]:
        """Run one resolved alternative: ``(exit code, output, aborted)``.

        ``aborted`` is True when the command could not be run to completion — a
        timeout or an OS-level failure. Those end the whole spec rather than
        falling through to the next alternative, because a metric parsed from a
        run that never finished is exactly the green this gate exists to refuse.
        """
        try:
            result = subprocess.run(
                [executable, *argv[1:]],
                capture_output=True,
                text=True,
                timeout=600,
                check=False,
            )
        except subprocess.TimeoutExpired:
            return 124, "Command timed out after 600 seconds", True
        except OSError as exc:
            return _EXIT_NOT_FOUND, f"Execution error: {exc}", True
        return result.returncode, (result.stdout or "") + (result.stderr or ""), False

    def _run(self, spec: CommandSpec) -> tuple[int, str]:
        combined = ""
        returncode = 0
        ran_any = False
        for index, argv in enumerate(spec.alternatives):
            if not argv:
                continue
            guard = spec.guard_for(index)
            if guard is not None and not Path(guard).exists():
                combined += f"Skipped {argv[0]}: {guard} not present\n"
                if not ran_any:
                    # Only while nothing has run: a later skip must not overwrite
                    # the exit code of an alternative that did the work.
                    returncode = _EXIT_NOT_APPLICABLE
                continue
            executable = shutil.which(argv[0])
            if executable is None:
                combined += f"Command not found: {argv[0]}\n"
                returncode = _EXIT_NOT_FOUND
                continue
            returncode, output, aborted = self._execute(executable, argv)
            combined += output
            if aborted:
                # The command existed and failed to run at all. Trying the next
                # alternative would report a metric no execution produced.
                return returncode, combined
            ran_any = True
            if returncode == 0:
                break
        if not ran_any and spec.alternatives:
            # Nothing applicable ever executed. Reporting the parsed metric here
            # would mean "0 findings" from a check that never happened.
            return returncode or _EXIT_NOT_APPLICABLE, combined
        if spec.swallow_exit and returncode != _EXIT_NOT_FOUND:
            # swallow_exit mirrors a trailing `|| true`: these tools exit non-zero
            # merely because they found something, and the gate judges the parsed
            # metric instead. It must NOT swallow 127. A tool that is not installed
            # yields a metric of 0, and "0 secrets" from a scan that never ran is
            # exactly the kind of green this project exists to refuse.
            return 0, combined
        return returncode, combined

    def _parse_passed_tests(self, output: str) -> int:
        """Read the test count from pytest's summary line.

        Taking the *first* match anywhere reads a test name: under ``-v`` a line
        like ``test_returns_none_on_404 PASSED`` satisfies ``(\\d+)\\s+passed``, so
        the gate recorded 404 for a suite of 785. With a ``>=`` threshold that
        baseline would have let the real count halve without complaint.

        The summary is the last such line, so the last match is the count.
        """
        for pattern in (r"(\d+)\s+passed", r"passed\s*=\s*(\d+)"):
            matches = re.findall(pattern, output, flags=re.IGNORECASE)
            if matches:
                return int(matches[-1])
        return 0

    def _parse_coverage(self, output: str) -> float:
        """Read the coverage percentage from a line that actually reports coverage.

        Matching any line containing "total" caught pytest's own progress marker:
        ``test_synthesis_multiple_repos_totals PASSED [ 93%]`` reported 93% for a
        run that covered 88.88%. Anchor on the two shapes coverage really emits,
        and only then fall back to the loose scan.
        """
        anchored = (
            r"total\s+coverage[:\s]+(\d+(?:\.\d+)?)%",  # pytest-cov's --cov-fail-under line
            r"^TOTAL\b.*?(\d+(?:\.\d+)?)%",  # the term-missing table's TOTAL row
        )
        for pattern in anchored:
            match = re.search(pattern, output, flags=re.IGNORECASE | re.MULTILINE)
            if match:
                return float(match.group(1))
        for line in output.splitlines():
            if any(token in line.lower() for token in ["total", "coverage", "covered"]):
                # Drop pytest's own progress marker ("... test_x_covered PASSED [ 42%]"):
                # a test name containing "covered" matches the token, and [ 42%] would
                # otherwise be read as coverage. Coverage percentages are never bracketed.
                stripped = re.sub(r"\[\s*\d+%\s*\]", "", line)
                # The pattern captures digits only, so float() cannot raise here —
                # the try/except this replaces was dead defensive code (PERF203).
                for value in re.findall(r"(\d+(?:\.\d+)?)%", stripped):
                    return float(value)
        return self._parse_coverage_report()

    def _parse_coverage_report(self) -> float:
        """Read the coverage percentage from a written XML report.

        `make test-cov` may emit only `--cov-report=xml`, in which case stdout
        carries no summary at all and the textual patterns above find nothing.
        """
        started = getattr(self, "_gate_started_at", None)
        for candidate in (Path("reports/coverage.xml"), Path("coverage.xml")):
            if not candidate.is_file():
                continue
            # A report older than this gate's own command was left by an earlier run
            # (or committed): its figure says nothing about the code under test and
            # would mask a regression. 1 s of slack absorbs coarse filesystem mtimes.
            if started is not None and candidate.stat().st_mtime < started - 1:
                print(f"WARNING|Coverage|stale report ignored: {candidate}")
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

    def _load_secrets_baseline(self) -> dict[str, Any] | None:
        """The repo's .secrets.baseline as a dict, or None if absent or unreadable."""
        path = Path(self.SECRETS_BASELINE_FILE)
        if not path.is_file():
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return None
        return data if isinstance(data, dict) and isinstance(data.get("results"), dict) else None

    def _known_secrets(self) -> set[tuple[str, str, str]] | None:
        """(filename, hashed_secret, type) of every finding the baseline acknowledges.

        Line numbers are deliberately ignored — they move with every edit above a
        finding, which is why detect-secrets itself matches on these three fields.
        ``None`` (no usable baseline) means "nothing is known": every finding counts.
        """
        baseline = self._load_secrets_baseline()
        if baseline is None:
            return None
        return {
            (str(filename), str(item.get("hashed_secret")), str(item.get("type")))
            for filename, items in baseline["results"].items()
            if isinstance(items, list)
            for item in items
            if isinstance(item, dict)
        }

    def _parse_secret_count(self, output: str) -> int:
        """Findings the scan reports that .secrets.baseline does not acknowledge.

        Counting every finding made the metric useless wherever a repo keeps test
        fixtures or audited false positives in its baseline: it measured the
        fixtures, not new leaks, and could only be compared with ``=``.
        """
        try:
            d = json.loads(output)
            results = d.get("results", {})
            known = self._known_secrets() or set()
            count = 0
            for filename, items in results.items():
                # A malformed entry is not evidence that nothing was found. Counting it
                # fails closed; the AttributeError it used to raise sent the parser to
                # the text fallback, which returned 0.
                for item in items if isinstance(items, list) else [items]:
                    if not isinstance(item, dict) or (
                        (str(filename), str(item.get("hashed_secret")), str(item.get("type"))) not in known
                    ):
                        count += 1
            return count
        except (json.JSONDecodeError, AttributeError, ValueError, TypeError):
            pass
        match = re.search(r"secrets?\s+found[:\s]+(\d+)", output, re.IGNORECASE)
        if match:
            return int(match.group(1))
        return 0

    def _parse_vuln_count(self, output: str) -> int | None:
        """Vulnerabilities found, or ``None`` when the output says nothing either way.

        The previous final ``return 0`` made a *failed* audit indistinguishable
        from a clean one: a run that crashed before auditing anything reported
        zero vulnerabilities, and ``0 ≤ baseline`` passed. Since the gate swallows
        the exit code for this tool — it exits non-zero merely for finding
        something — the exit code could not tell them apart either. ``None`` means
        "not measured", and :meth:`_compare` fails closed on it.
        """
        match = re.search(r"found\s+(\d+)\s+vulnerabilit", output, re.IGNORECASE)
        if match:
            return int(match.group(1))
        count = len(re.findall(r"(?:GHSA|CVE)-\S+", output))
        if count:
            return count
        if re.search(r"no\s+known\s+vulnerabilit", output, re.IGNORECASE):
            return 0
        return None

    def _parse_metric(self, gate_name: str, exit_code: int, output: str) -> int | float | None:
        """Gate name -> its metric parser, as a table: a new gate is a row, not a branch."""
        parsers: dict[str, Callable[[], int | float | None]] = {
            "Tests": lambda: self._parse_passed_tests(output),
            "Coverage": lambda: self._parse_coverage(output),
            "Lint": lambda: self._parse_warning_count(output),
            "Types": lambda: self._parse_error_count(output),
            "Build": lambda: 0 if exit_code == 0 else 1,
            "Secrets": lambda: self._parse_secret_count(output),
            "VulnDeps": lambda: self._parse_vuln_count(output),
        }
        parse = parsers.get(gate_name)
        return parse() if parse is not None else None

    def _compare(self, current: int | float | None, target: int | float | None, operator: str) -> bool:
        """Apply a comparison operator, failing closed on anything it cannot judge.

        ``None`` on either side means the metric was never measured. Comparing it
        would either raise or, worse, pass — a ``≤`` gate reads an unmeasured
        metric as satisfied. An unknown operator fails the same way.
        """
        if current is None or target is None:
            return False
        compare = _COMPARISONS.get(operator)
        return compare(current, target) if compare is not None else False

    def _run_gate(self, gate_name: str, key: str, metric_name: str, default_spec: CommandSpec) -> dict[str, Any]:
        raw = self.config.get("commands", {}).get(key)
        # Inherit the default's swallow_exit: overriding *which* command runs must
        # not silently change whether its exit code gates. Moving security_vulns
        # into config dropped it once, and pip-audit finding a CVE failed the gate.
        spec = CommandSpec.parse(raw, swallow_exit=default_spec.swallow_exit) if raw is not None else default_spec
        print(f"RUN_GATE|{gate_name}|{spec.display()}")
        # Read back by _parse_coverage_report: a report older than this is stale.
        self._gate_started_at = time.time()
        exit_code, output = self._run(spec)
        metric = self._parse_metric(gate_name, exit_code, output)
        return {
            "gate": gate_name,
            "command": spec.display(),
            "exit_code": exit_code,
            "metric_name": metric_name,
            "metric": metric,
            "timestamp": datetime.now().isoformat(),
            "output": output,
        }

    @staticmethod
    def _for_baseline(result: dict[str, Any]) -> dict[str, Any]:
        """Strip the captured command output from a gate result.

        The baseline is meant to be read, diffed and committed. Keeping ``output``
        made it 344 KB, of which ~120 KB was a full detect-secrets dump plus entire
        pytest logs — a transcript, not a record. Only ``metric`` and ``valid`` are
        ever read back by :meth:`verify`; the untrimmed result still goes to the
        last-report file, which is gitignored.
        """
        return {key: value for key, value in result.items() if key != "output"}

    def _write_report(self, report: dict[str, Any]) -> None:
        with open(self.last_report_path, "w", encoding="utf-8") as handle:
            json.dump(report, handle, indent=2)

    def baseline(self) -> bool:
        print("BASELINE|START")
        baseline_data: dict[str, Any] = {
            "recorded_at": datetime.now().isoformat(),
            "gates": {},
            "valid": True,
        }

        all_ok = True
        for gate_name, key, metric_name, _default_op, default_cmd in self.gates:
            result = self._run_gate(gate_name, key, metric_name, default_cmd)
            baseline_data["gates"][gate_name] = self._for_baseline(result)
            if result["exit_code"] != 0:
                all_ok = False
                baseline_data["valid"] = False
            status = "PASS" if result["exit_code"] == 0 else "FAIL"
            print(
                f"GATE_RESULT|{gate_name}|{status}|metric={result['metric']}|exit={result['exit_code']}|mode=baseline"
            )

        with open(self.baseline_path, "w", encoding="utf-8") as handle:
            # Sorted, and newline-terminated: the file is committed, so the shared
            # json-sorter hook would otherwise rewrite it and leave a diff behind
            # every single time the baseline is recorded.
            json.dump(baseline_data, handle, indent=2, sort_keys=True)
            handle.write("\n")

        report = {
            "mode": "baseline",
            "overall": "PASS" if all_ok else "FAIL",
            "baseline_file": str(self.baseline_path),
            "gates": baseline_data["gates"],
        }
        self._write_report(report)

        if all_ok:
            print("OVERALL_RESULT|PASS")
            return True

        print("OVERALL_RESULT|FAIL")
        print("ERROR: baseline contains failing gates; fix quality checks before using this baseline")
        return False

    def verify(self) -> int:
        """Compare the current metrics with the baseline; return the process exit code.

        ``EXIT_PASS`` when every gate holds, ``EXIT_FAIL`` on any regression, and
        ``EXIT_NOT_EVALUATED`` when there is no baseline: nothing was compared, so the
        run must not read as a pass.
        """
        print("VERIFY|START")
        if not self.baseline_path.exists():
            report = {
                "mode": "verify",
                "overall": "SKIP",
                "reason": "no_baseline",
                "baseline_file": str(self.baseline_path),
            }
            self._write_report(report)
            print("OVERALL_RESULT|SKIP")
            print(
                f"ERROR: not evaluated — no baseline at {self.baseline_path}; nothing was checked "
                f"(exit {EXIT_NOT_EVALUATED}). Run 'make quality-gate-baseline' and commit the file."
            )
            return EXIT_NOT_EVALUATED

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

            passed = True
            reason = "ok"

            if not baseline_valid:
                passed = False
                reason = "invalid_baseline"
            elif current.get("exit_code", 1) != 0:
                passed = False
                reason = "command_failed"
            else:
                try:
                    passed = self._compare(current_metric, target, operator)
                    if not passed:
                        reason = "metric_regression"
                except Exception:
                    passed = False
                    reason = "comparison_error"

            if not passed:
                all_passed = False

            status = "PASS" if passed else "FAIL"
            print(
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
            print("OVERALL_RESULT|PASS")
            return EXIT_PASS

        print("OVERALL_RESULT|FAIL")
        return EXIT_FAIL


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 quality_gate.py [baseline|verify]")
        sys.exit(1)

    command = sys.argv[1].strip().lower()
    quality_gate = QualityGate()

    if command == "baseline":
        sys.exit(EXIT_PASS if quality_gate.baseline() else EXIT_FAIL)
    if command == "verify":
        sys.exit(quality_gate.verify())

    print(f"Unknown command: {command}")
    sys.exit(1)


if __name__ == "__main__":
    main()
