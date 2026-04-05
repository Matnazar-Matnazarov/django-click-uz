"""
Ruff check va format — bitta skript orqali ishga tushirish.
Ishlatish: python ruff_check.py
"""

import subprocess
import sys
from pathlib import Path

COMMANDS = [
    ["ruff", "check", ".", "--fix"],
    ["ruff", "format", "."],
]
ROOT = Path(__file__).resolve().parent


def main() -> int:
    for cmd in COMMANDS:
        print(f"👉 Running: {' '.join(cmd)}")
        ret = subprocess.run(cmd, cwd=ROOT)
        if ret.returncode != 0:
            return ret.returncode
    return 0


if __name__ == "__main__":
    sys.exit(main())
