#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MARS_DIR = ROOT.parent / "MARS"
ASM = ROOT / "blackjack.asm"
COMMAND = ["java", "-cp", str(MARS_DIR), "Mars", "nc", str(ASM)]

ERROR_MARKERS = (
    "Runtime exception",
    "Processing terminated due to errors",
    "Exception in thread",
    "fetch address not aligned",
    "invalid char input",
)


def lines(*items):
    return "\n".join(str(item) for item in items) + "\n"


TESTS = [
    {
        "name": "main menu exits cleanly",
        "input": lines(3),
        "must_contain": ["WELCOME TO ASM-BLACKJACK"],
    },
    {
        "name": "invalid main menu option recovers",
        "input": lines(9, 3),
        "must_contain": ["Please choose a valid option"],
    },
    {
        "name": "settings language menu returns to main menu",
        "input": lines(2, 1, 3),
        "must_contain": ["LANGUAGE MENU", "WELCOME TO ASM-BLACKJACK"],
    },
    {
        "name": "spanish language menu exits",
        "input": lines(2, 2, 3),
        "must_contain": ["BIENVENIDO A ASM-BLACKJACK"],
    },
    {
        "name": "bet too high is rejected then exits after one hand",
        "input": lines(1, 999999, 10, "", "", 2, 2, 2, 2, 2, 2),
        "must_contain": ["You cannot bet more than the amount of money that you have"],
    },
    {
        "name": "play one hand and stay",
        "input": lines(1, 2, "", "", 2, 2, 2, 2, 2, 2, 2, 2),
        "must_contain": ["The match is going to start", "The dealer shows"],
    },
    {
        "name": "hit path handles repeated hits",
        "input": lines(1, 2, "", "", 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2),
        "must_contain": ["You have got", "OPTIONS"],
    },
    {
        "name": "double path handles card draw",
        "input": lines(1, 2, "", "", 3, 2, 2, 2, 2, 2, 2),
        "must_contain": ["You have got", "The sum of your cards"],
    },
]


def run_test(test):
    completed = subprocess.run(
        COMMAND,
        input=test["input"],
        text=True,
        capture_output=True,
        cwd=ROOT,
        timeout=10,
    )
    output = completed.stdout + completed.stderr
    failures = []

    if completed.returncode != 0:
        failures.append(f"exit code {completed.returncode}")

    for marker in ERROR_MARKERS:
        if marker in output:
            failures.append(f"found error marker: {marker}")

    for expected in test.get("must_contain", []):
        if expected not in output:
            failures.append(f"missing expected text: {expected}")

    return failures, output


def main():
    failed = 0
    for test in TESTS:
        try:
            failures, output = run_test(test)
        except subprocess.TimeoutExpired as exc:
            failures = ["timed out"]
            output = (exc.stdout or "") + (exc.stderr or "")

        if failures:
            failed += 1
            print(f"FAIL {test['name']}")
            for failure in failures:
                print(f"  - {failure}")
            print("  output tail:")
            for line in output.splitlines()[-20:]:
                print(f"    {line}")
        else:
            print(f"PASS {test['name']}")

    print(f"\n{len(TESTS) - failed}/{len(TESTS)} tests passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
