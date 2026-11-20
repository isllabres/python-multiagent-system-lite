#!/usr/bin/env python3
"""Pull a newer tagged release of this layer into the current project.

Reads `.opencode/layer.json` for which upstream repo and version this
project's copy came from, lists that repo's tags over plain `git
ls-remote` (no clone, no auth needed for a public repo), and - if a
newer one exists - downloads that tag's public GitHub archive and
overwrites `.opencode/` and `AGENTS.md` with it. `.opencode/commit-style.md`
and `.opencode/token-usage.jsonl` are never touched: they're this
project's own state, not part of the layer.

Nothing is committed. Run from the project root and review the result
like any other change - `.opencode/opencode.json` especially, if you've
customized its permissions block.
"""
from __future__ import annotations

import argparse
import io
import json
import subprocess
import sys
import tarfile
import urllib.request
from pathlib import Path

DEFAULT_REPO = "isllabres/python-multiagent-system-lite"
LAYER_JSON_PATH = Path(".opencode/layer.json")
SKIP_PATHS = {".opencode/commit-style.md", ".opencode/token-usage.jsonl"}


def _is_payload_path(path: str) -> bool:
    return path == "AGENTS.md" or path.startswith(".opencode/")


def _parse_version(tag: str) -> tuple[int, int, int]:
    parts = tag.lstrip("v").split(".")
    if len(parts) < 1 or len(parts) > 3:
        raise ValueError(tag)
    nums = tuple(int(p) for p in parts)
    return nums + (0,) * (3 - len(nums))


def load_layer_info(path: Path) -> dict:
    if not path.exists():
        print(f"{path} not found - bootstrapping it against {DEFAULT_REPO}.")
        return {"repo": DEFAULT_REPO, "version": "v0.0.0"}
    return json.loads(path.read_text())


def save_layer_info(path: Path, info: dict) -> None:
    path.write_text(json.dumps(info, indent=2) + "\n")


def list_remote_tags(repo: str) -> list[str]:
    url = f"https://github.com/{repo}.git"
    result = subprocess.run(
        ["git", "ls-remote", "--tags", "--refs", url],
        capture_output=True,
        text=True,
        check=True,
    )
    tags = []
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        ref = line.split("\t")[-1]
        tag = ref.removeprefix("refs/tags/")
        if tag:
            tags.append(tag)
    return tags


def latest_tag(tags: list[str]) -> str | None:
    parsed = []
    for tag in tags:
        try:
            parsed.append((_parse_version(tag), tag))
        except ValueError:
            continue
    if not parsed:
        return None
    parsed.sort()
    return parsed[-1][1]


def download_payload(repo: str, tag: str, dest: Path) -> list[str]:
    url = f"https://github.com/{repo}/archive/refs/tags/{tag}.tar.gz"
    request = urllib.request.Request(url, headers={"User-Agent": "python-multiagent-system-lite-updater"})
    with urllib.request.urlopen(request) as response:
        data = response.read()

    written = []
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tar:
        names = tar.getnames()
        if not names:
            return written
        root = names[0].split("/", 1)[0]
        for member in tar.getmembers():
            if not member.isfile():
                continue
            relative = Path(member.name).relative_to(root)
            relative_str = str(relative)
            if not _is_payload_path(relative_str) or relative_str in SKIP_PATHS:
                continue
            target = dest / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            extracted = tar.extractfile(member)
            if extracted is None:
                continue
            target.write_bytes(extracted.read())
            written.append(relative_str)
    return written


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="only report the latest available tag, don't download or write anything",
    )
    parser.add_argument(
        "--to",
        metavar="TAG",
        help="update (or roll back) to this exact tag instead of the latest one",
    )
    args = parser.parse_args()

    info = load_layer_info(LAYER_JSON_PATH)
    repo, current = info["repo"], info["version"]

    try:
        tags = list_remote_tags(repo)
    except subprocess.CalledProcessError as exc:
        print(f"could not list tags for {repo}: {exc}", file=sys.stderr)
        sys.exit(1)

    target = args.to or latest_tag(tags)
    if target is None:
        print(f"no valid version tags found on {repo}.")
        return

    if args.check:
        print(f"installed: {current}  latest: {target}  ({repo})")
        return

    if not args.to and _parse_version(target) <= _parse_version(current):
        print(f"already on {current}, which is the latest tag on {repo}.")
        return

    print(f"updating {repo} from {current} to {target}...")
    written = download_payload(repo, target, Path("."))
    if not written:
        print("downloaded the release but found nothing under .opencode/ or AGENTS.md - nothing changed.", file=sys.stderr)
        return

    info["version"] = target
    save_layer_info(LAYER_JSON_PATH, info)
    print(f"wrote {len(written)} file(s), updated {LAYER_JSON_PATH} to {target}.")
    print("Nothing committed - review with `git status`/`git diff` before committing.")


if __name__ == "__main__":
    main()
