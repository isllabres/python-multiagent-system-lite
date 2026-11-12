#!/usr/bin/env python3
"""Append this project's OpenCode token/cost usage to a local JSONL log.

Reads the project's own session history via the `opencode` CLI
(`session list`, `session export`) - nothing is tracked independently of
what OpenCode already records. Run from the project root, since
`session list` scopes itself to the current project.

Known limitation: `session list` only returns top-level sessions. If a
subagent's child session (the implementer's or reviewer's own session,
delegated to via the task tool) isn't listed there too, its usage won't
be picked up automatically - verify this against a real multi-round
session before trusting the totals, and pass its id to `--session-id`
as a manual fallback if it's missing.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_LOG_PATH = Path(__file__).resolve().parents[1] / "token-usage.jsonl"


def _run(*args: str) -> str:
    result = subprocess.run(["opencode", *args], capture_output=True, text=True, check=True)
    return result.stdout


def _logged_session_ids(log_path: Path) -> set[str]:
    if not log_path.exists():
        return set()
    ids = set()
    for line in log_path.read_text().splitlines():
        if line.strip():
            ids.add(json.loads(line)["session_id"])
    return ids


def _list_session_ids() -> list[str]:
    output = _run("session", "list")
    return [line.split("\t", 1)[0] for line in output.splitlines() if line.strip()]


def _session_record(session_id: str) -> dict:
    info = json.loads(_run("session", "export", session_id))
    session = info["info"]
    agents = sorted(
        {
            m["agent"]
            for m in info.get("messages", [])
            if m.get("type") == "assistant" and m.get("agent")
        }
    )
    model = session.get("model", {})
    return {
        "logged_at": datetime.now(timezone.utc).isoformat(),
        "session_id": session["id"],
        "title": session.get("title"),
        "agents": agents,
        "provider": model.get("providerID"),
        "model": model.get("id"),
        "cost": session.get("cost", 0),
        "tokens": session.get("tokens", {}),
        "outcome": session.get("outcome"),
        "session_created": session.get("time", {}).get("created"),
        "session_updated": session.get("time", {}).get("updated"),
    }


def collect(log_path: Path, extra_session_ids: list[str] | None = None) -> list[dict]:
    already_logged = _logged_session_ids(log_path)
    candidate_ids = _list_session_ids() + (extra_session_ids or [])
    new_records = []
    for session_id in candidate_ids:
        if session_id in already_logged:
            continue
        try:
            new_records.append(_session_record(session_id))
            already_logged.add(session_id)
        except (subprocess.CalledProcessError, KeyError, json.JSONDecodeError) as exc:
            print(f"skipped {session_id}: {exc}", file=sys.stderr)
    if new_records:
        with log_path.open("a") as f:
            for record in new_records:
                f.write(json.dumps(record) + "\n")
    return new_records


def summarize(log_path: Path) -> None:
    if not log_path.exists():
        print("No usage logged yet.")
        return
    totals: dict[tuple[str, str], dict[str, float]] = defaultdict(
        lambda: {"sessions": 0, "cost": 0.0, "input": 0, "output": 0}
    )
    for line in log_path.read_text().splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        key = (",".join(record.get("agents") or ["?"]), record.get("model") or "?")
        bucket = totals[key]
        bucket["sessions"] += 1
        bucket["cost"] += record.get("cost") or 0
        bucket["input"] += (record.get("tokens") or {}).get("input", 0)
        bucket["output"] += (record.get("tokens") or {}).get("output", 0)

    print(f"{'agent(s)':<24} {'model':<28} {'sessions':>8} {'cost':>10} {'in tok':>10} {'out tok':>10}")
    for (agents, model), bucket in sorted(totals.items()):
        print(
            f"{agents:<24} {model:<28} {bucket['sessions']:>8} "
            f"{bucket['cost']:>10.4f} {bucket['input']:>10} {bucket['output']:>10}"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--summary",
        action="store_true",
        help="print totals grouped by agent and model instead of collecting new sessions",
    )
    parser.add_argument(
        "--session-id",
        action="append",
        dest="session_ids",
        default=[],
        help="also try to log this session id, in case it's a child session session list doesn't surface (repeatable)",
    )
    parser.add_argument(
        "--log-path",
        type=Path,
        default=DEFAULT_LOG_PATH,
        help="override the log file location (default: .opencode/token-usage.jsonl)",
    )
    args = parser.parse_args()

    if args.summary:
        summarize(args.log_path)
        return

    records = collect(args.log_path, extra_session_ids=args.session_ids)
    if not records:
        print("No new sessions to log.")
        return
    for record in records:
        agents = ",".join(record["agents"]) or "unknown agent"
        print(f"logged {record['session_id']} ({agents}, {record['model']}): cost={record['cost']} tokens={record['tokens']}")


if __name__ == "__main__":
    main()
