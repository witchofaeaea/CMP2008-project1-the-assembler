#!/usr/bin/env python3
"""Auto-grader for the assembler skeleton.

This script runs assembler_skeleton.py to generate files under outputs/ and
compares them to the reference files under answers/. Each matching test case
receives 5 points.
"""

from __future__ import annotations

import argparse
import difflib
import importlib.util
import os
import sys
from pathlib import Path


def read_lines(path: Path) -> list[str]:
    with path.open("r", newline="") as fh:
        return [line.rstrip("\r\n") for line in fh]


def compare_files(generated: Path, expected: Path) -> tuple[bool, str]:
    if not generated.exists():
        return False, f"missing output file: {generated.name}"

    actual = read_lines(generated)
    expected_lines = read_lines(expected)
    if actual == expected_lines:
        return True, ""

    diff = difflib.unified_diff(
        expected_lines,
        actual,
        fromfile=f"expected/{expected.name}",
        tofile=f"outputs/{generated.name}",
        lineterm="",
    )
    return False, "\n" + "\n".join(diff)


def read_student_info(path: Path) -> dict[str, str]:
    info = {"Name": "", "Surname": "", "ID": ""}
    if not path.exists():
        return info

    with path.open("r", newline="") as fh:
        for _ in range(20):
            line = fh.readline()
            if not line:
                break
            stripped = line.strip()
            if not stripped.startswith("#"):
                continue

            content = stripped.lstrip("#").strip()
            if ":" not in content:
                continue

            key, value = content.split(":", 1)
            key = key.strip()
            if key in info:
                info[key] = value.strip()
    return info


def run_assembler(module_path: Path) -> bool:
    if not module_path.exists():
        print(f"ERROR: target file not found: {module_path}", file=sys.stderr)
        return False

    spec = importlib.util.spec_from_file_location("grader_target", module_path)
    if spec is None or spec.loader is None:
        print(f"ERROR: failed to load target module from {module_path}", file=sys.stderr)
        return False

    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as exc:
        print(f"ERROR: failed to import {module_path.name}: {exc}", file=sys.stderr)
        return False

    if not hasattr(module, "main"):
        print(f"ERROR: target module {module_path.name} has no main() function", file=sys.stderr)
        return False

    try:
        module.main()
    except SystemExit as exc:
        if exc.code != 0:
            print(f"ERROR: {module_path.name} exited with non-zero status", file=sys.stderr)
            return False
    except Exception as exc:
        print(f"ERROR: {module_path.name}.main() raised an exception: {exc}", file=sys.stderr)
        return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Auto-grade assembler module output against expected answers.")
    parser.add_argument(
        "--target",
        default="assembler_skeleton.py",
        help="Python source file to run for assembly (default: assembler_skeleton.py)",
    )
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent
    target_path = (project_root / args.target).resolve()
    answers_dir = project_root / "answers"
    outputs_dir = project_root / "outputs"

    print(f"Using target module: {target_path.name}")
    student_info = read_student_info(target_path)
    print("Student info:")
    print(f"  Name:    {student_info['Name'] or 'N/A'}")
    print(f"  Surname: {student_info['Surname'] or 'N/A'}")
    print(f"  ID:      {student_info['ID'] or 'N/A'}")
    print()

    print(f"Running {target_path.name}...")
    if not run_assembler(target_path):
        print("Aborting grading due to assembler failure.")
        return 1

    if not answers_dir.exists():
        print(f"ERROR: answers directory not found: {answers_dir}", file=sys.stderr)
        return 1

    expected_files = sorted(answers_dir.glob("*.hex"))
    if not expected_files:
        print(f"ERROR: no answer files found in {answers_dir}", file=sys.stderr)
        return 1

    weights = {
        "test_r_format.hex": 12,
        "test_b_format.hex": 12,
        "test_i_format.hex": 10,
        "test_all.hex": 15,
        "test_d_format.hex": 25,
        "test_cb_format.hex": 26,
    }
    total_score = 0
    max_score = sum(weights.get(path.name, 0) for path in expected_files)
    failed_tests: list[str] = []
    print("Grading rubric:")
    for name, pts in weights.items():
        if any(path.name == name for path in expected_files):
            print(f"  {name}: {pts} points")
    print(f"Total available: {max_score} points")
    print()

    for expected_path in expected_files:
        generated_path = outputs_dir / expected_path.name
        points = weights.get(expected_path.name, 0)
        passed, message = compare_files(generated_path, expected_path)
        if passed:
            total_score += points
            print(f"PASS  {expected_path.name}: +{points} points")
        else:
            failed_tests.append(expected_path.name)
            print(f"FAIL  {expected_path.name}: +0 points")
            print(message)
            print()

    print("---")
    print(f"Total score: {total_score}/{max_score}")
    if failed_tests:
        print("Failed tests:")
        for name in failed_tests:
            print(f"  - {name}")
    if total_score == max_score:
        print("All tests passed!")
    else:
        print("Some tests failed. Inspect the diffs above.")

    return 0 if total_score == max_score else 2


if __name__ == "__main__":
    raise SystemExit(main())
