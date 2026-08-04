#!/usr/bin/env python3
"""Génère des commits d'activité sur ce dépôt."""

from __future__ import annotations

import argparse
import json
import os
import random
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

LOG = Path(__file__).parent / "activity.json"


def run(*args: str) -> None:
    try:
        subprocess.run(args, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as exc:
        print(exc.stderr.strip(), file=sys.stderr)
        raise


def append_entry() -> int:
    entries = json.loads(LOG.read_text()) if LOG.exists() else []
    entries.append({"ts": datetime.now(timezone.utc).isoformat(timespec="seconds")})
    entries = entries[-500:]
    LOG.write_text(json.dumps(entries, indent=2) + "\n")
    return len(entries)


def has_staged_changes() -> bool:
    return subprocess.run(["git", "diff", "--cached", "--quiet"]).returncode != 0


def make_commit() -> None:
    count = append_entry()
    run("git", "add", str(LOG))
    if has_staged_changes():
        run("git", "commit", "-m", f"chore: update activity log ({count})")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--min", type=int, default=1)
    parser.add_argument("--max", type=int, default=3)
    parser.add_argument("--skip-chance", type=float, default=0.0)
    args = parser.parse_args()

    email = os.environ.get("COMMIT_EMAIL")
    if not email:
        print("COMMIT_EMAIL absent : sans email vérifié, aucun carré vert.", file=sys.stderr)
        return 1

    if random.random() < args.skip_chance:
        print("Exécution sautée.")
        return 0

    run("git", "config", "user.email", email)
    run("git", "config", "user.name", os.environ.get("COMMIT_NAME") or "KD6-3.7")

    for _ in range(random.randint(args.min, args.max)):
        make_commit()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())